#!/usr/bin/python
# -*- coding: utf-8 -*-

# Created on 03.09.2013

"""
.. currentmodule:: PyroMP

Callbacks to a Service
----------------------

Derive the class from :class:`CallbackService` instead of
:class:`Service` to support callback functionality. All methods decorated
with :obj:`callback` are wrapped by :class:`CallbackFunction`.

Here is an example:

.. code-block:: python

    class TestService(CallbackService):

        @callback
        def callback_function(self, *args, **kwargs):
            # do some stuff

.. note::
    For an extensive example see :ref:`callback_service_example`.

.. warning::
    It is not possible to start a :class:`CallbackService` in multiplex mode,
    because that would lead to deadlocks.

Callbacks to a process/thread that is no Service
------------------------------------------------

To perform the communication with Pyro4 there must be a
:class:`CallbackServer` running. Use the with-statement:

.. code-block:: python

    with CallbackServer():
        # do some stuff

Or start and stop the server manually:

.. code-block:: python

    CallbackServer.start()
    # do some stuff
    CallbackServer.stop()

Classes which should provide callback functionality have to be derived
from :class:`CallbackObject` and the callback functions have to be
decorated with :obj:`callback` to be wrapped by :class:`CallbackFunction`.

Here is an example:

.. code-block:: python

    class TestObject(CallbackObject):

        @callback
        def callback_function(self, *args, **kwargs):
            # do some stuff

.. note::
    For an extensive example see :ref:`callback_object_example`.


Using callbacks
---------------

Just call :func:`~CallbackFunction.call`.
See also :ref:`callback_object_example` or :ref:`queued_callback_example`..

Events
------

Events join several callbacks together. To get callbacks from that event you
just have to :func:`~Event.register`:

.. image:: images/cb_register.png

If :func:`~Event.trigger` is called, the call is forwarded to all
registered callbacks:

.. image:: images/event_trigger.png

The caller doesn't have to care how many callbacks are registered.
Doesn't matter if there are no registered callbacks at all.

.. note:: Each callback is executed in its own thread and errors are logged.

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
"""

from __future__ import print_function, unicode_literals, division

# Built-in
import uuid
import functools
import weakref
from multiprocessing import Lock
from threading import Thread

# Extern
import Pyro4
from six.moves import copyreg

# Intern
from . import log_server as log
from PyroMP.server import ServerProcess
from PyroMP.service import Service
from PyroMP.errors import (CallbackServerAlreadyRunningError,
                           CallbackServerNotRunningError)


# copied from Pyro4.core, because could not be imported
def _pyroObjectSerializer(self):
    """reduce function that automatically replaces Pyro objects by a Proxy"""
    daemon = getattr(self, "_pyroDaemon", None)
    if daemon:
        # only return a proxy if the object is a registered pyro object
        return Pyro4.core.Proxy, (daemon.uriFor(self),)
    else:
        return self.__reduce__()


class _CallbackServer(ServerProcess):

    def __init__(self):
        super(_CallbackServer, self).__init__(thread=True,
                                             logging=True,
                                             daemon=True)
        self._daemon = None

    def _stop_thread(self, daemon):
        while self._queue.get() != self.CLOSE:
            pass

        daemon.shutdown()

    def _serve(self):
        logger = self.get_logger("CALLBACK_SERVER_THREAD")

        logger.debug("Create pyro daemon")
        self._daemon = Pyro4.Daemon()

        logger.debug("Put ready on the queue")
        self._queue.put(self.READY)

        logger.debug("Create and start thread to stop the server")
        t = Thread(target=self._stop_thread, args=(self._daemon, ))
        t.daemon = True
        t.start()

        logger.debug("Start request loop")
        try:
            self._daemon.requestLoop()
        except Pyro4.errors.ConnectionClosedError as exc:
            logger.error("The connection was unexpectedly closed")
            raise exc

    def register(self, obj):
        try:
            # use weakref to enable garbage collection
            # for callback objects
            self._daemon.register(weakref.proxy(obj),
                                 obj.id())
        except AttributeError:
            raise CallbackServerNotRunningError()
        else:
            # because of weakref we have to modify the object
            # and register a function for pickle
            # to use the autoproxy feature
            copyreg.pickle(type(obj), _pyroObjectSerializer)
            obj._pyroDaemon = self._daemon
            obj._pyroId = obj.id()

    def unregister(self, obj):
        try:
            self._daemon.unregister(obj.id())
        except AttributeError:
            raise CallbackServerNotRunningError()


class CallbackServer(object):
    """Manages a thread with a daemon to serve callbacks

    Implements the
    `singleton pattern <http://en.wikipedia.org/wiki/Singleton_pattern>`_.
    """

    _LOGGER_NAME = "CALLBACK_SERVER"
    _server = None

    @classmethod
    def register(cls, cb_func):
        """Register the given :class:`CallbackFunction` at the server

        Parameters
        ----------
        cb_func : :class:`CallbackFunction`
            Function to be registered
        """
        try:
            cls._server.register(cb_func)
        except AttributeError:
            raise CallbackServerNotRunningError()

    @classmethod
    def unregister(cls, cb_func):
        """Register the given :class:`CallbackFunction` at the server

        Parameters
        ----------
        cb_func : :class:`CallbackFunction`
            Function to be registered
        """
        try:
            cls._server.unregister(cb_func)
        except AttributeError:
            raise CallbackServerNotRunningError()

    @classmethod
    def start(cls):
        """Starts the server

        Raises
        ------
        exc : :class:`~PyroMP.errors.CallbackServerAlreadyRunningError`
            If the server is already running
        """
        if cls._server is None:
            logger = log.create_logger(cls._LOGGER_NAME)
            cls._server = _CallbackServer()
            logger.debug("Start server")
            cls._server.start()
        else:
            raise CallbackServerAlreadyRunningError

    @classmethod
    def stop(cls):
        """Stops the server

        Raises
        ------
        exc : :class:`~PyroMP.errors.CallbackServerNotRunningError`
            If the server is not running
        """
        try:
            logger = log.create_logger(cls._LOGGER_NAME)
            logger.debug("Stop server")
            cls._server.stop()
            logger.debug("Clear daemon variable")
            cls._server = None
        except AttributeError:
            raise CallbackServerNotRunningError()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


CALLBACK_ATTR_NAME = "_remote_callback"


def callback(func):
    """Marks class method as callback function
    """
    setattr(func, CALLBACK_ATTR_NAME, True)
    return func


class CallbackObject(object):
    """Wraps all methods decorated with :obj:`callback`
    with a :class:`CallbackFunction`
    """

    def __init__(self, **kwargs):
        super(CallbackObject, self).__init__(**kwargs)
        for name in dir(self):
            attr = getattr(self, name)
            callback = getattr(attr, CALLBACK_ATTR_NAME, False)
            if callback:
                func_name = "{}.{}".format(self.__class__.__name__, name)
                setattr(self, name, CallbackFunction(attr, func_name))


class CallbackService(Service):
    """Bases: :class:`Service`

    Service that wraps all methods decorated with :obj:`callback`
    with a :class:`CallbackFunction`
    """

    def init_resources(self):
        super(CallbackService, self).init_resources()
        daemon = getattr(self, "_pyroDaemon")
        for name in dir(self):
            attr = getattr(self, name)
            callback = getattr(attr, CALLBACK_ATTR_NAME, False)
            if callback:
                func_name = "{}.{}".format(self.__class__.__name__, name)
                setattr(self, name, CallbackFunction(attr, func_name, daemon))


class CallbackFunction(object):
    """Wraps a function and registers at the :class:`CallbackServer` or
    the given :class:`Pyro4.Daemon`.
    """

    def __init__(self, func, name, daemon=None):
        """
        Parameters
        ----------
        func : callable
            Function to be wrapped
        daemon : :class:`Pyro4.Daemon`
            (optional) if provided, registered at that :class:`~Pyro4.Daemon`
            instead of registering at the :class:`CallbackServer`

        Notes
        -----

        Can be called like normal functions

        Callbacks are called using autoproxy feature of Pyro4.
        As Pyro4 does only support function calls, an additional
        :func:`~CallbackFunction.call` function is provided.
        """
        functools.update_wrapper(self, func)
        self.__id = uuid.uuid4().hex
        self.__func = func
        self.__name = name
        self._is_service_callback = daemon is not None
        if daemon:
            daemon.register(self)
        else:
            CallbackServer.register(self)

    def __del__(self):
        if not self._is_service_callback:
            CallbackServer.unregister(self)

    def __call__(self, *args, **kwargs):
        self.__func(*args, **kwargs)

    def id(self):
        """Returns a unique id for this callback"""
        return self.__id

    def to_string(self):
        """Returns the name of the function and object"""
        return self.__name

    @Pyro4.callback
    def call(self, *args, **kwargs):
        """Calls the wrapped function with given ``args`` and ``kwargs``.
        """
        self.__call__(*args, **kwargs)


class Event(object):

    def __init__(self):
        self._callbacks = {}
        self._lock = Lock()

    def get_logger(self):
        return log.create_logger("Event")

    def register(self, callback):
        """Adds the callback to this event"""
        with self._lock:
            logger = self.get_logger()
            logger.debug("Get callback id")
            id_ = callback.id()
            name = callback.to_string()
            logger.debug("Register " + name + " with id: " + id_)
            self._callbacks[id_] = (callback, name)

    def unregister(self, callback):
        """Removes the callback from this event"""
        with self._lock:
            logger = self.get_logger()
            logger.debug("Get callback id")
            id_ = callback.id()
            name = callback.to_string()
            logger.debug("Unregister " + name + " with id: " + id_)
            del(self._callbacks[id_])

    def trigger(self, *args, **kwargs):
        """Calls all registered callback functions.
        The args and kwargs are forwarded to each of them"""
        with self._lock:
            logger = self.get_logger()
            for callback, name in self._callbacks.values():
                logger.debug("Call " + repr(callback))
                thread = Thread(target=self.__asynccall,
                                args=(callback, name, args, kwargs))
                thread.setDaemon(True)
                thread.start()

    def __asynccall(self, callback, name, args, kwargs):
        try:
            logger = self.get_logger()
            try:
                callback.call(*args, **kwargs)
            except Pyro4.errors.ConnectionClosedError:
                logger.debug("Connection lost. REBINDING...")
                callback._pyroReconnect(2)
                callback.call(*args, **kwargs)

        except:
            logger = self.get_logger()
            logger.error("".join(Pyro4.util.getPyroTraceback()))
