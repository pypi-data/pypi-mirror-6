'''The :mod:`pulsar.apps.pubsub` module implements a middleware
handler for the Publish/Subscribe pattern. The middleware can be used to
synchronise pulsar actors across processes and machines.

.. epigraph::

    In software architecture, publish/subscribe is a messaging pattern where
    senders of messages, called publishers, do not program the messages to
    be sent directly to specific receivers, called subscribers.
    Instead, published messages are characterised into classes, without
    knowledge of what, if any, subscribers there may be. Similarly,
    subscribers express interest in one or more classes, and only receive
    messages that are of interest, without knowledge of what, if any,
    publishers there are.

    -- wikipedia_


When using this middleware, one starts by creating a :class:`PubSub` handler::

    from pulsar.apps.pubsub import PubSub

    pubsub = PubSub(backend=None, ...)

The ``backend`` parameter is needed in order to select the backend
to use. If not supplied, the default ``local://`` backend is used.

Usage
==============

A pubsub handler can be passed to different process domain and therefore it
can be used to synchronise pulsar actors.

A typical usage is when one needs to serve a websocket on a multiprocessing
web server such as the :ref:`pulsar WSGI server <apps-wsgi>`.
For example, the :ref:`websocket chat server <tutorials-chat>` uses a pubsub
handler to propagate a message received from an http client to all
the clients currently listening for messages.

Since these clients may be served by different web server processes, the
pubsub handler is an handy tool for synchronisation.

Registering a client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a new client connects to the websocket, the ``on_open`` method of a
:ref:`websocket handler <apps-ws>` add the websocket to the set of
clients of the ``pubsub`` handler::

    def on_open(self, websocket):
        self.pubsub.add_client(PubSubClient(websocket))

The ``PubSubClient`` is a :class:`Client` wrapper around the ``websocket``
which calls the ``websocket`` write method when called::

    class PubSubClient(pubsub.Client):

    def __init__(self, connection):
        self.connection = connection

    def __call__(self, channel, message):
        if channel == 'webchat':
            self.connection.write(message)


Publishing
~~~~~~~~~~~~~~~~~~~~~~

When a new message is received by the websocket ``on_message`` method,
we use the ``pubsub`` handle to publish the message::

    def on_message(self, websocket, msg):
        self.pubsub.publish('webchat', msg)


And the rest is taken care of by the callables ``PubSubClient`` which write
the message to all listening websocket clients.


PubSub handler
========================

.. autoclass:: PubSub
   :members:
   :member-order: bysource


PubSub Client
======================

.. autoclass:: Client
   :members:
   :member-order: bysource


PubSub backend
========================

.. autoclass:: PubSubBackend
   :members:
   :member-order: bysource


.. _wikipedia: http://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern
'''
import logging

import pulsar
from pulsar import get_actor
from pulsar.utils.pep import to_string
from pulsar.utils.log import local_property


LOGGER = logging.getLogger('pulsar.pubsub')


class Client(object):
    '''Interface for a client of :class:`PubSub` handler.

    Instances of this :class:`Client` are callable object and are
    called once a new message has arrived from a subscribed channel.
    The callable accepts two parameters:

    * ``channel`` the channel which originated the message
    * ``message`` the message
    '''
    def __call__(self, channel, message):
        raise NotImplementedError


class PubSub(object):
    '''Publish/Subscribe paradigm handler.

    .. attribute:: backend

        The :class:`PubSubBackend` for this handler.

    .. attribute:: encoder

        Optional callable which encode the messages before they are published.


    A backend handler is a picklable instance and therefore it can be
    passed to different process domains.
    '''
    def __init__(self, backend=None, encoder=None, **params):
        be = PubSubBackend.make(backend=backend, **params)
        self.backend = PubSubBackend.get(be.id, backend=be)
        self.encoder = encoder

    @property
    def clients(self):
        '''Set of all clients for this :class:`PubSub` handler.'''
        return self.backend.clients

    @property
    def id(self):
        return self.backend.id

    @property
    def name(self):
        return self.backend.name

    def add_client(self, client):
        '''Add a new ``client`` to the set of all :attr:`clients`. Clients
must have the ``write`` method available. When a new message is received
from the publisher, the :meth:`broadcast` method will notify all
:attr:`clients` via the ``write`` method.'''
        self.backend.add_client(client)

    def remove_client(self, client):
        '''Remove *client* from the set of all :attr:`clients`.'''
        self.backend.remove_client(client)

    def channel(self, channel):
        return self.backend.channel(channel)

    def publish(self, channel, message):
        '''Publish a ``message`` to ``channel``. It invokes the
:meth:`PubSubBackend.publish` method after the message has been encoded
via the :attr:`encoder` callable (if available).'''
        if self.encoder:
            message = self.encoder(message)
        return self.backend.publish(channel, message)

    def subscribe(self, *channels):
        '''Invoke the :meth:`PubSubBackend.subscribe` method.'''
        return self.backend.subscribe(*channels)

    def unsubscribe(self, *channels):
        '''Invoke the :meth:`PubSubBackend.unsubscribe` method.'''
        return self.backend.unsubscribe(*channels)

    def close(self):
        '''Close connections'''
        return self.backend.close()


class PubSubBackend(pulsar.Backend):
    '''Publish/Subscribe :class:`pulsar.apps.Backend` interface.
    '''
    @local_property
    def clients(self):
        '''The set of clients for this :class:`PubSub` handler.'''
        return set()

    @classmethod
    def path_from_scheme(cls, scheme):
        return 'pulsar.apps.pubsub.%s' % scheme

    def add_client(self, client):
        '''Add a new ``client`` to the set of all :attr:`clients`. Clients
must have the ``write`` method available. When a new message is received
from the publisher, the :meth:`broadcast` method will notify all
:attr:`clients` via the ``write`` method.'''
        self.clients.add(client)

    def remove_client(self, client):
        '''Remove *client* from the set of all :attr:`clients`.'''
        self.clients.discard(client)

    def channel(self, channel):
        return channel

    def publish(self, channel, message):
        '''Publish a ``message`` into ``channel``.

Must be implemented by subclasses.'''
        raise NotImplementedError

    def subscribe(self, *channels):
        '''Subscribe to the server which publish messages.

A series of one or more ``channels`` to subscribe to must be passed to this
method which must be implemented by subclasses.'''
        raise NotImplementedError

    def unsubscribe(self, *channels):
        '''Un-subscribe from the server which publish messages.

An optional series of ``channels`` can be passed. If no channels are passed,
it unsubscribed from all channels.

Must be implemented by subclasses.'''
        raise NotImplementedError

    def broadcast(self, channel, message):
        '''Broadcast ``message`` to all :attr:`clients`.'''
        remove = set()
        channel = to_string(channel)
        message = self.decode(message)
        clients = tuple(self.clients)
        for client in clients:
            try:
                client(channel, message)
            except IOError:
                remove.add(client)
            except Exception:
                LOGGER.exception('Exception while processing pub/sub client. '
                                 'Removing it.')
                remove.add(client)
        self.clients.difference_update(remove)

    def close(self):
        '''Close this :class:`PubSubBackend`.'''
        actor = get_actor()
        actor.params.pubsub.pop(self.id, None)
        return self.unsubscribe()

    def decode(self, message):
        '''Convert message to a string.'''
        return to_string(message)

    @classmethod
    def get(cls, id, actor=None, backend=None):
        actor = actor or get_actor()
        if not actor:
            raise RuntimeError('Cannot initialise pubsub when no actor.')
        if 'pubsub' not in actor.params:
            actor.params.pubsub = {}
        be = actor.params.pubsub.get(id)
        if not be and backend:
            be = backend
            actor.params.pubsub[id] = be
        return be
