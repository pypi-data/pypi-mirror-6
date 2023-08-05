import socket
import sys
import math
import logging
from functools import partial, reduce
from threading import Lock

from pulsar.utils.pep import get_event_loop, new_event_loop, itervalues, range
from pulsar.utils.internet import is_socket_closed

from .defer import Failure, is_failure, multi_async

from .protocols import Producer, ConnectionProducer

__all__ = ['ConnectionPool', 'Client', 'Request']


class Request(object):
    '''A :class:`Client` request.

    A request object is hashable an it is used to select
    the appropriate :class:`ConnectionPool` for the client request.

    .. attribute:: address

        The socket address of the remote server

    .. attribute:: release_connection

        When ``True`` a protocol consumer release the connection back to the
        :class:`ConnectionPool` once done with the request.

        Default: ``True``
    '''
    inp_params = None
    release_connection = True

    def __init__(self, address, timeout=0):
        self.address = address
        self.timeout = timeout

    @property
    def key(self):
        '''Attribute used for selecting the appropriate
:class:`ConnectionPool`'''
        return (self.address, self.timeout)

    @property
    def ssl(self):
        '''A transport layer security context or ``True``.

        Used to create SSL/TLS connections.
        '''
        return False

    def encode(self):
        raise NotImplementedError

    def connect(self, event_loop, connection):
        '''Called by a :class:`Client` when a new connection is needed.
        '''
        host, port = self.address
        _, connection = yield event_loop.create_connection(
            lambda: connection, host, port, ssl=self.ssl)
        # wait for the connection_made event
        yield connection.event('connection_made')
        # starts the new request
        connection.current_consumer.start(self)


class ConnectionPool(ConnectionProducer):
    '''A :class:`Producer` of of active connections for client protocols.

    It maintains a live set of :class:`Connection`.

    .. attribute:: address

        Address to connect to
    '''
    def __init__(self, request, **params):
        params['timeout'] = request.timeout
        self.lock = Lock()
        super(ConnectionPool, self).__init__(**params)
        self._address = request.address
        self._available_connections = set()

    def __repr__(self):
        return repr(self.address)
    __str__ = __repr__

    @property
    def address(self):
        return self._address

    @property
    def available_connections(self):
        '''Number of available connection in the pool.

        Available connections are not currently in-use and therefore they can
        be selected when the :meth:`get_or_create_connection` method is
        invoked.
        '''
        return len(self._available_connections)

    def release_connection(self, connection, response=None):
        '''Releases the ``connection`` back to the pool.

        This function remove the ``connection`` from the set of concurrent
        connections and add it to the set of available connections.

        :parameter connection: The connection to release
        :parameter response: Optional :class:`ProtocolConsumer` which consumed
            the connection. It is passed to the
            :meth:`Client.can_reuse_connection` method to check if the
            connection can be reused.
        '''
        with self.lock:
            self._concurrent_connections.discard(connection)
            if connection.producer.can_reuse_connection(connection, response):
                self._available_connections.add(connection)

    def get_or_create_connection(self, client, connection=None):
        '''Get or create a new connection for ``client``.

        If a ``connection`` is given and either

        * the connection is in the set of available connections
        * the connection is in the set of concurrent connections but without
          a protocol consumer

        then it is chosen ahead of others in the pool.
        '''
        stale_connections = []
        with self.lock:
            if connection:
                if connection in self._available_connections:
                    self._available_connections.remove(connection)
                elif not (connection in self._concurrent_connections and
                          connection.current_consumer is None):
                    connection = None
                if connection:
                    sock = connection.sock
                    closed = is_socket_closed(sock)
                    if closed:
                        if sock:
                            stale_connections.append(connection)
                        connection = None
                    else:
                        self._concurrent_connections.add(connection)
            if not connection:
                try:
                    closed = True
                    while closed:
                        connection = self._available_connections.pop()
                        sock = connection.sock
                        closed = is_socket_closed(sock)
                        if closed and sock:
                            stale_connections.append(connection)
                except KeyError:
                    connection = None
                else:
                    # we have a connection, lets added it to the concurrent set
                    self._concurrent_connections.add(connection)
        for sc in stale_connections:
            sc.transport.close()
        if connection is None:
            # build the new connection
            connection = self.new_connection(client.consumer_factory,
                                             producer=client)
        return connection


def release_response_connection(response):
    '''Added as a post_request callback to release the connection.

    :parameter response: the :class:`ProtocolConsumer` calling this function
    once done with its request.

    If the :class:`Request` associated with the protocol consumer has
    the :attr:`Request.release_connection` set to ``False`` the connection
    is not released to the connection pool.
    '''
    request = response.request
    connection = response.connection
    if connection:
        connection.set_consumer(None)
        if getattr(request, 'release_connection', False):
            key = response.request.key
            pool = response.producer.connection_pools.get(key)
            if not pool:
                connection.logger.error(
                    'Could not fined connection pool to release %s',
                    connection)
            else:
                pool.release_connection(connection, response)
    return response


class Client(Producer):
    '''A client for several remote servers of the same type.

    It is a :class:`Producer` which handles one or more
    :class:`ConnectionPool` of asynchronous connections to a server.

    It has the ``finish`` :ref:`one time event <one-time-event>` fired when
    calling the :meth:`close` method.

    In the same way as the :class:`Server` class, :class:`Client` has four
    :ref:`many time events <many-times-event>`:

    * ``connection_made`` a new :class:`Connection` is made.
    * ``pre_request``, can be used to add information to the request
      to send to the remote server.
    * ``post_request``, fired when a full response has been received. It can be
      used to post-process responses.
    * ``connection_lost`` a connection dropped.

    Most initialisation parameters have sensible defaults and don't need to be
    passed for most use-cases (the only exception is the
    :meth:`consumer_factory` callable which must be specified).

    Additionally, these parameters can be set as class attributes to override
    defaults.

    :param max_connections: set the :attr:`Producer.max_connections` attribute.
    :param timeout: set the :attr:`Producer.timeout` attribute.
    :param connection_factory: set the :attr:`Producer.connection_factory`
        attribute.
    :param force_sync: set the :attr:`force_sync` attribute.
    :param event_loop: optional :class:`EventLoop` which set the
        :attr:`event_loop`.
    :param connection_pool: optional factory which set the
        :attr:`connection_pool`.
        The :attr:`connection_pool` can also be set at class level.
    :param max_reconnect: set the :attr:`max_reconnect` attribute.
    :param consumer_factory: set the :meth:`consumer_factory` callable.
    :parameter client_version: optional version string for this
        :class:`Client`.

    .. attribute:: event_loop

        The :class:`EventLoop` for this :class:`Client`. Can be ``None``.
        The preferred way to obtain the event loop is via the
        :meth:`get_event_loop` method rather than accessing this attribute
        directly.

    .. attribute:: force_sync

        Force a :ref:`synchronous client <tutorials-synchronous>`, that is a
        client which has it own :class:`EventLoop` and blocks until a response
        is available.

        Default: `False`
    '''
    max_reconnect = 1
    '''Can reconnect on socket error.'''
    connection_pools = None
    '''Dictionary of :class:`ConnectionPool`.

    If initialized at class level it will remain as a class attribute,
    otherwise it will be an instance attribute.
    '''
    connection_pool = None
    '''Factory of :class:`ConnectionPool`.'''
    consumer_factory = None
    '''A factory of :class:`ProtocolConsumer` for sending and consuming
    data.
    '''
    client_version = ''
    '''An optional version for this client.'''
    reconnecting_gap = 2
    '''Reconnecting gap in seconds.'''
    ONE_TIME_EVENTS = ('finish',)
    MANY_TIMES_EVENTS = ('connection_made', 'pre_request', 'post_request',
                         'connection_lost')

    def __init__(self, connection_factory=None, timeout=None,
                 client_version=None, connection_pool=None, trust_env=True,
                 max_connections=None, consumer_factory=None, event_loop=None,
                 max_reconnect=None, force_sync=False, **params):
        super(Client, self).__init__(connection_factory=connection_factory,
                                     timeout=timeout,
                                     max_connections=max_connections)
        self._closed = False
        self.trust_env = trust_env
        self.client_version = client_version or self.client_version
        self.connection_pool = (connection_pool or self.connection_pool or
                                ConnectionPool)
        if consumer_factory:
            self.consumer_factory = consumer_factory
        if self.connection_pools is None:
            self.connection_pools = {}
        if max_reconnect:
            self.max_reconnect = max_reconnect
        self.force_sync = force_sync
        self.event_loop = event_loop
        self.setup(**params)

    def __repr__(self):
        return self.__class__.__name__
    __str__ = __repr__

    @property
    def concurrent_connections(self):
        '''Total number of concurrent connections.'''
        return reduce(lambda x, y: x + y, (p.concurrent_connections for p in
                                           itervalues(self.connection_pools)),
                      0)

    @property
    def available_connections(self):
        '''Total number of available connections.'''
        return reduce(lambda x, y: x + y, (p.available_connections for p in
                                           itervalues(self.connection_pools)),
                      0)

    @property
    def closed(self):
        '''``True`` if the :meth:`close` was invoked on this :class:`Client`.

        A closed :class:`Client` cannot send :meth:`request` to remote
        servers.
        '''
        return self._closed

    def setup(self, **params):
        '''Setup the client.

        Invoked at the end of initialisation with the additional parameters
        passed. By default it does nothing.'''
        pass

    def get_event_loop(self):
        '''Return the :class:`EventLoop` used by this :class:`Client`.

        The event loop can be set during initialisation. If :attr:`force_sync`
        is ``True`` a specialised event loop is created.
        '''
        if self.event_loop:
            return self.event_loop
        elif self.force_sync:
            logger = logging.getLogger(('pulsar.%s' % self).lower())
            self.event_loop = new_event_loop(iothreadloop=False,
                                             logger=logger)
            return self.event_loop
        else:
            return get_event_loop()

    def build_consumer(self, consumer_factory=None):
        '''Override the :meth:`Producer.build_consumer` method.

        Add a ``post_request`` handler to release the connection back to
        the connection pool.
        '''
        consumer_factory = consumer_factory or self.consumer_factory
        consumer = consumer_factory()
        consumer.copy_many_times_events(self)
        consumer.bind_event('post_request', release_response_connection)
        return consumer

    def request(self, *args, **params):
        '''Abstract method for creating a :class:`Request`.

        The request is sent to a remote server via the :meth:`response`
        method. This method **must be implemented by subclasses** and should
        return a :class:`ProtocolConsumer` via invoking the
        :meth:`response` method::

            def request(self, ...):
                ...
                request = ...
                return self.response(request)

        '''
        raise NotImplementedError

    def response(self, request, response=None, new_connection=True,
                 connection=None):
        '''Sends a ``request`` to the remote server.

        Once a ``request`` object has been constructed, the :meth:`request`
        method can invoke this method to build the :class:`ProtocolConsumer`
        and start the response.
        There should not be any reason to override this method.
        This method is run on this client event loop (obtained via the
        :meth:`get_event_loop` method) thread.

        :parameter request: a custom :class:`Request` for the :class:`Client`.
        :parameter response: a :class:`ProtocolConsumer` to reuse, otherwise
            ``None`` (Default).
        :parameter new_connection: ``True`` if a new connection is required
            via the :meth:`get_connection` method. Default ``True``.
        :return: a :class:`ProtocolConsumer` obtained form
            :attr:`consumer_factory`.
        '''
        event_loop = self.get_event_loop()
        if response is None or response.has_finished:
            response = self.build_consumer()
        inp_params = request.inp_params
        if isinstance(inp_params, dict):
            response.bind_events(**inp_params)
        if response.event('pre_request').has_fired():
            # pre request event already fired, this is an updated request
            # TODO: document this feature.
            # Used by redis client for example
            response.silence_event('pre_request')
            response._request = request
        else:   # A new request
            event_loop.call_soon_threadsafe(self._response, event_loop,
                                            response, request, new_connection,
                                            connection)
            if self.force_sync and not event_loop.is_running():
                event_loop.run_until_complete(response.on_finished,
                                              timeout=request.timeout)
                return response.on_finished.get_result()
        return response

    def get_connection(self, request, connection=None):
        '''Returns a suitable :class:`Connection` for ``request``.

        :param request: a :class:`Request` used to select the appropriate
            :class:`ConnectionPool` for obtaining the connection.
        :param connection: optional :class:`Connection` which may be reused.

        First checks if an available open connection can be used.
        Alternatively it creates a new connection by invoking the
        :meth:`ConnectionPool.get_or_create_connection` method on the
        appropiate connection pool.

        If a new connection is created, the connection won't be yet
        ``connected`` with end-point.

        Thread safe.
        '''
        pool = self.connection_pools.get(request.key)
        if pool is None:
            connection = None
            pool = self.connection_pool(
                request,
                max_connections=self.max_connections,
                connection_factory=self.connection_factory)
            self.connection_pools[request.key] = pool
        return pool.get_or_create_connection(self, connection)

    def update_parameters(self, parameter_list, params):
        '''Update ``params`` with attributes from this :class:`Client`.

        :param parameter_list: an iterable over parameter names to add to
            ``params`` if ``params`` does not already have them.
        :param params: dictionary of parameters to update.
        :return: an updated copy of params.
        '''
        nparams = params.copy()
        for name in parameter_list:
            if name not in params:
                nparams[name] = getattr(self, name)
        return nparams

    def close_connections(self, async=True):
        '''Close all connections in each :attr:`connection_pools`.

        :param async: if ``True`` flush the write buffer before closing (same
            as :class:`SocketTransport.close` method).
        :return: a :class:`Deferred` called back once all connections are
            closed.
        '''
        all = []
        for p in self.connection_pools.values():
            all.append(p.close_connections(async=async))
        return multi_async(all)

    def close(self, async=True, timeout=5):
        '''Close all connections.

        Fire the ``finish`` :ref:`one time event <one-time-event>` once done.
        Return the :class:`Deferred` fired by the ``finish`` event.
        '''
        if not self.closed:
            self._closed = True
            event = self.close_connections(async)
            event.add_both(partial(self.fire_event, 'finish'))
            event.set_timeout(timeout, self.get_event_loop())
        return self.event('finish')

    def abort(self):
        ''':meth:`close` all connections without waiting for active connections
        to finish.'''
        self.close(async=False)

    #def reconnect_time_lag(self, lag):
    #    lag = self.reconnect_time_lag*(math.log(lag) + 1)
    #    return round(lag, 1)

    def timeit(self, times, *args, **kwargs):
        '''Send ``times`` requests asynchronously and evaluate the time
        taken to obtain all responses. In the standard implementation
        this method will open ``times`` :class:`Connection` with the
        remote server.
        Usage::

            client = Client(...)
            multi = client.timeit(100, ...)
            response = yield multi
            multi.total_time

        :return: a :class:`MultiDeferred` which results in the list of results
          for the individual requests. Its :attr:`MultiDeferred.total_time`
          attribute indicates the number of seconds taken (once the deferred
          has been called back).
        '''
        results = []
        for _ in range(times):
            r = self.request(*args, **kwargs)
            if hasattr(r, 'on_finished'):
                r = r.on_finished
            results.append(r)
        return multi_async(results)

    #   INTERNALS

    def _response(self, event_loop, response, request, new_connection,
                  connection):
        # Actually execute the request. This method is always called on the
        # event loop thread
        try:
            conn = connection or response.connection
            if new_connection or conn is None:
                # Get the connection for this request
                conn = self.get_connection(request, conn)
                conn.set_consumer(response)
            if conn.transport is None:
                # There is no transport, we need to connect with server first
                event_loop.async(request.connect(
                    event_loop, conn)).add_errback(response.finished)
            else:
                response.start(request)
            return
        except Exception:
            exc_info = sys.exc_info()
        response.finished(Failure(exc_info))
