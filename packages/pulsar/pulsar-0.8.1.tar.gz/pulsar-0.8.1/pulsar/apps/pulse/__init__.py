'''The :mod:`pulsar.apps.pulse` module is a django application for running
a django web site with pulsar. Add it to the list of your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...,
        'pulsar.apps.pulse',
        ...
    )

and run the site via the ``pulse`` command::

    python manage.py pulse

Check the :ref:`django chat example <tutorials-django>` for a django chat
application served by a multiprocessing pulsar server.
'''
