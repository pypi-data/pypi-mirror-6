#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created on 21.08.2013

'''
.. currentmodule:: PyroMP

What is a Service?
------------------

Basically a service is just an object. But a service can also be executed in a
separate process or thread.

Define a Service
----------------

Just derive a class from :class:`Service` and it's done.

.. code-block:: python

    class TestService(Service):

        def do_something(self, *args, **kwargs)
            # do some stuff

There are some class attributes which can be used to adjust the service behaviour.

    - **Service.LOGGING**: Enable/disable logging (default: True)
    - **Service.THREADED**: If ``True`` a thread is started instead of a
      process (default: False)
    - **Service.DAEMON**: Flag is forwarded to the deamon flag of
      the created :attr:`Process <multiprocessing.Process.daemon>` or
      :attr:`Thread <threading.Thread.daemon>` (default: True)

As you can see in :ref:`use service`,
support for the with statement is provided.
The downside is, everytime using ``with`` the constructor is called.
There may be some initialization stuff that is only
necessary when creating that service in another process or thread.
For that purpose :func:`~Service.init_resources` can be used
as well as :func:`~Service.close_resources` to clean up everything
before the process gets stopped.

For example a service that needs a file:

.. code-block:: python

    class FileService(Service):

        def init_resources(self):
            super(FileService, self).init_resources()
            # open file
            self._file = open('..')

        def close_resources(self):
            super(FileService, self).close_resources()
            # close file
            self._file.close()

        def do_something(self, *args, **kwargs)
            # do some stuff


.. _use service:

Use a Service
-------------

The easiest way to use a service is the ``with``-statement:

.. code-block:: python

    with TestService() as service:
        service.do_something()

- If the service is not running the service is started and
  stopped automatically after the with-block.
- If the service is running and managed by the current process, it is not
  started again but stopped after the with-block.
- If the service is running and managed by another process, only a connection
  is initialized and released after the with-block.
  The service continues running.

.. note::
    The process that starts a service is the one that manages it.

Another way is to start and stop the service as well as connecting to the
service manually:

.. code-block:: python

    TestService.start()

    # ...

    with TestService.get_connection() as service:
        service.do_something()

    # ...

    TestService.stop()

You can either get a synchronous or asynchronous connection which is controlled
by the ``async`` parameter of the :class:`constructor <Service>` or of
:func:`~Service.get_connection`.

.. note:: A :class:`Service` can be used as described above, in
    combination with :class:`QueuedService` or as a normal Python object. But
    in the latter case you have to care that :func:`~Service.init_resources`
    and :func:`~Service.close_resources` are called, if necessary.
    (See :ref:`local_service_example`)

Synchronous
***********

A synchronous call is a blocking call like a normal function call. If you have
an asynchronous connection, it is also possible to do synchronous calls using
the ``sync`` attribute.

.. code-block:: python

    with TestService.get_connection(async=False) as service:
        service.do_something()

    with TestService.get_connection(async=True) as service:
        service.sync.do_something()


Asynchronous
************

An asynchronous call is a not blocking call and returns a
:class:`Pyro4.futures.FutureResult` object. If you have a synchronous connection, it
is also possible to do asynchronous calls using the ``async`` attribute:

.. code-block:: python

    with TestService.get_connection(async=True) as service:
        service.do_something()

    with TestService.get_connection(async=False) as service:
        service.async.do_something()

.. warning::
    Take care that all asynchronous calls are finished before you stop a
    service or they will not processed and raise a timeout error.

.. _autoproxy:

Autoproxy
---------

:mod:`Pyro4` has a feature called `Autoproxying`_. This feature is enabled for
PyroMP services. If a running :class:`Service` object is passed to another process.
It is replaced by a :class:`~Pyro4.core.Proxy` to it.

.. _Autoproxying: http://pythonhosted.org/Pyro4/servercode.html#autoproxying

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

# Built-in
import time

# Extern
import Pyro4
import mock
import six

# Intern
from PyroMP.errors import (NameServerError,
                           ServiceNotAvailableError)

Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED = set(['pickle'])
Pyro4.config.COMMTIMEOUT = 120


class _PriorityMeta(type):

    def __init__(self, class_name, parents, attrs):
        super(_PriorityMeta, self).__init__(class_name, parents, attrs)
        self._PRIORITY_DICT = {}
        for name in dir(self):
            if not name.startswith("_"):
                attr = getattr(self, name, None)
                if callable(attr):
                    self._PRIORITY_DICT[name] = getattr(attr, "_queue_priority", 0)


class Service(six.with_metaclass(_PriorityMeta, object)):
    """Base class for all services
    """

    LOGGING = True
    DAEMON = True
    THREADING = False

    def __init__(self, multiplex=False, async=True, **kwargs):
        """
        Parameters
        ----------
        multiplex : bool
            Determines the servertype when using ``with``
                - True -> multiplex
                - False -> threaded

            See
            `Pyro4 documentation <http://pythonhosted.org/Pyro4/servercode.html#server-types-and-object-concurrency-model>`_

        async : bool
            Determines if the connection returned using ``with``
            is synchronous or asynchronous
        """
        super(Service, self).__init__(**kwargs)
        self.__multiplex = multiplex
        self.__async = async

    def init_resources(self):
        """Called when the service process is starting after everything
        else was set up
        """
        pass

    def get_logger(self):
        """Returns the logger of this class or just a logger
        stub, if ``LOGGING`` is ``False``
        """
        if self.LOGGING:
            return log.create_logger(self.get_pyro_name())
        else:
            return mock.Mock()

    def close_resources(self):
        """Called before stopping the service process
        """
        pass

    def __enter__(self):
        logger = self.get_logger()
        logger.debug("Start server")
        self.start(self.__multiplex)
        logger.debug("Get connection")
        self.__conn = self.get_connection(self.__async)
        logger.debug("Connect")
        self.__conn.connect()
        logger.debug("Return connection")
        return self.__conn

    def __exit__(self, exc_type, exc_value, traceback):
        self.__conn.disconnect()
        self.stop()

    @classmethod
    def get_pyro_name(cls):
        """Returns a name for registering at a :class:`~PyroMP.NameServer`
        """
        return cls.__name__.upper()

    @classmethod
    def get_connection(cls, async=True):
        """
        Parameters
        ----------
        async : bool
            Determines if the connection is synchronous or asynchronous
        """
        return ServiceConnection(cls, async)

    @classmethod
    def is_running(cls):
        """Checks if the :class:`Service` is running

        Returns
        -------
        running : bool
            ``True`` if it is running ``False`` otherwise
        """
        return server.ServiceProcessManager.is_running(cls)

    @classmethod
    def start(cls, multiplex=False):
        """Starts the service if not already running

        Parameters
        ----------
        multiplex : bool
            Determines the servertype.
                - True -> multiplex
                - False -> threaded

            See
            `Pyro4 documentation <http://pythonhosted.org/Pyro4/servercode.html#server-types-and-object-concurrency-model>`_

        Notes
        -----
        Only the process that has started a service is able to stop it.
"""
        server.ServiceProcessManager.start(cls, multiplex)

    @classmethod
    def stop(cls):
        """Stops the service if running and managed by this process"""
        server.ServiceProcessManager.stop(cls)


class QtService(Service):
    """Bases: :class:`PyroMP.Service`

    A :class:`Service` providing a Qt and Pyro4 event loop.

    Notes
    -----
    The service is stopped when all windows are closed
    """

    def qt_main(self):
        """Main function to initialize the gui.
        If no window is shown, the service will be stopped immediately.

        Has to be reimplemented in derived classes.

        .. warning::
            You have to connect to :class:`events <PyroMP.Event>` or other
            PyroMP stuff in the :func:`init_resources` function
            or your program will deadlock
        """
        raise NotImplementedError()

    @classmethod
    def wait_for(cls):
        """Wait until the service is not running anymore
        (e.g. windows has been closed)
        """
        while cls.is_running():
            time.sleep(0.1)


class ServiceConnection(object):
    """Manages an :class:`~Pyro4.Proxy` for the given service
    """

    _own_attributes = ("connect", "disconnect")

    def __init__(self, service, async):
        """
        Notes
        -----

        Do not use the constructor manually, use
        :func:`Service.get_connection` instead

        with-statement can be used to connect and disconnect, too
        """
        self._service = service
        self._proxy = None
        self._async = None
        self._async_flag = async

    def get_logger(self):
        if self._service.LOGGING:
            return log.create_logger(self._service.get_pyro_name() + "_CONNECTION")
        else:
            return mock.Mock()

    def __getattr__(self, name):
        if name in self._own_attributes or name.startswith("_"):
            raise AttributeError()

        if self._proxy is None:
            raise AttributeError()

        if self._async_flag:
            if name == "sync":
                return self._proxy
            else:
                return getattr(self._async, name)
        else:
            if name == "async":
                return self._async
            else:
                return getattr(self._proxy, name)

    def disconnect(self):
        """Releases the connection to the service
        """
        self._proxy._pyroRelease()
        self._proxy = None
        self._async = None

    def connect(self):
        """Connects to the service

        Raises
        ------
        exc : :class:`~PyroMP.errors.NameServerError`
            If no :class:`Nameserver` is running
        exc : :class:`~PyroMP.errors.ServiceNotAvailableError`
            If the service is not running
        """
        logger = self.get_logger()
        try:
            logger.debug("Try to connect to service")
            self._connect_to_service()

        except NameServerError:
            logger.error("NameServerError")
            raise

        except ServiceNotAvailableError:
            logger.error("ServiceNotAvailableError")
            raise
        else:
            logger.debug("Connected")

    def _connect_to_service(self):
        logger = self.get_logger()

        logger.debug("Locate name server")
        ns = server.NameServer.locate()

        try:
            logger.debug("Lookup uri")
            uri = ns.lookup(self._service.get_pyro_name())
        except Pyro4.errors.NamingError:
            raise ServiceNotAvailableError
        finally:
            ns._pyroRelease()

        logger.debug("Create proxy")
        self._proxy = Pyro4.Proxy(uri)
        self._async = Pyro4.async(self._proxy)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

# Avoid error due to circular import
import PyroMP.log_server as log
import PyroMP.server as server
