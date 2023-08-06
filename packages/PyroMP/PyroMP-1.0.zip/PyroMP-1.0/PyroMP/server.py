#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created on 21.08.2013
'''
.. currentmodule:: PyroMP

NameServer
----------

Each :class:`Service` is registered at the :class:`NameServer`.
The name which is used for registering is the return value of
:func:`Service.get_pyro_name`. By default this is the class name
converted to upper. Therefore it is not possible to run 2 services
of the same class.
If this is required, derive a class with a different name.
Another possibility would be to overwrite :func:`Service.get_pyro_name`.

.. note::
    It is possible to :func:`~NameServer.disable` the :class:`NameServer`,
    e.g. to force :mod:`~PyroMP.log_server.create_logger` to use a local logger,
    when running a simple script concurrent to a service-based application.
    (See :ref:`local_service_example`)

.. hint::
    If you want to connect to a service, but not import it, you can define
    a class with the same name and no functionality, which is derived of
    :class:`Service`, and you are able to connect to the service.

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function

# Built-in
import mock
import select
import sys
import time
import multiprocessing as mp
import multiprocessing.dummy as mp_dummy
from threading import Thread

# Extern
import Pyro4
from six.moves import queue

# Intern
from PyroMP.errors import ServerError, NameServerError
from .service import QtService

Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED = set(['pickle'])


# Get remote traceback for exceptions
# and log uncatched exceptions
def excepthook(ex_type, ex_value, ex_tb):
    logger = log.get_server_root_logger()
    logger.error("".join(Pyro4.util.getPyroTraceback(ex_type, ex_value, ex_tb)))
    Pyro4.util.excepthook(ex_type, ex_value, ex_tb)
sys.excepthook = excepthook


class ServerProcess(object):

    READY = "ready"
    CLOSE = "close"
    ERROR = "error"

    def __init__(self, daemon, logging, thread):
        self._process = None
        self._daemon = daemon
        self._logging = logging

        self._thread = thread
        self._queue = mp.Queue()

    def join(self):
        self._process.join()

    def running(self):
        return self._process is not None and self._process.is_alive()

    def start(self):
        logger = self.get_logger("ServerProcess")

        if self._thread:
            _mp = mp_dummy
        else:
            _mp = mp
        self._process = _mp.Process(target=self._serve)
        self._process.daemon = self._daemon
        logger.debug("Start process")
        self._process.start()
        # wait for server to start
        logger.debug("Wait for server to start")
        try:
            response = self._queue.get(timeout=30)
            if  response == self.ERROR:
                text = "Process could not be started"
                logger.error(text)
                raise ServerError(text)
            elif response != self.READY:
                text = "Unknown response: {!r}".format(response)
                logger.error(text)
                raise ServerError(text)
        except queue.Empty:
            raise ServerError("Communication timeout")
        logger.debug("{} has started".format(self.__class__.__name__))
        time.sleep(1)

    def stop(self):
        self._queue.put(self.CLOSE)
        self.join()

    def get_logger(self, name):
        if self._logging:
            return log.create_logger(name)
        else:
            return mock.Mock()

    def _serve(self):
        self._queue.put(self.READY)
        raise NotImplementedError()


class NameServer(object):
    """Manages a thread which runs
    a :class:`Pyro4.naming.NameServer`

    `Further information <http://pythonhosted.org/Pyro4/nameserver.html>`_
    """

    _server = None
    _running = None
    _enabled = True

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    @classmethod
    def enable(cls):
        """Enables the NameServer functionality
        """
        cls._enabled = True

    @classmethod
    def disable(cls):
        """Disables the NameServer functionality

        If disabled, :func:`locate` will always raise an error and
        :func:`start` won't do anything.
        """
        cls._enabled = False

    @classmethod
    def locate(cls):
        """Works like :func:`~Pyro4.naming.locateNS`, but supports
        enabling and disabling.

        Raises
        ------
        exc : :class:`~PyroMP.errors.NameServerError`
            If no NameServer is found
        """
        if cls._enabled and (cls._running is None or cls._running):
            try:
                cls._running = True
                return Pyro4.locateNS()
            except Pyro4.naming.NamingError:
                cls._running = False
                raise NameServerError
        else:
            raise NameServerError

    @classmethod
    def start(cls):
        """If there is no
        :class:`Pyro4.naming.NameServer`
        running, a thread is started that runs one
        """
        if cls._enabled:
            try:
                cls.locate()
            except NameServerError:
                cls._server = NameServerProcess()
                cls._server.start()
                cls._running = True

    @classmethod
    def stop(cls):
        """Stops the name server,
        if started in this process
        """
        if cls._server is not None:
            cls._server.stop()
            cls._server = None
            cls._running = False


class NameServerProcess(ServerProcess):

    def __init__(self):
        # nameserver is necessary for logging
        # so disable logging
        super(NameServerProcess, self).__init__(daemon=True,
                                               logging=False,
                                               thread=False)

    def _serve(self):
        # we're using custom classes, so need to use pickle
        Pyro4.config.SERIALIZERS_ACCEPTED = set(['pickle'])

        _, daemon, bcserver = Pyro4.naming.startNS()

        self._queue.put(self.READY)

        t = Thread(target=self._stop_thread, args=(daemon, bcserver))
        t.daemon = True
        t.start()

        daemon.requestLoop()

    def _stop_thread(self, daemon, bcserver):
        while self._queue.get() != self.CLOSE:
            pass

        daemon.shutdown()
        if bcserver is not None:
            bcserver.close()


from .callback import CallbackService


class ServiceServerProcess(ServerProcess):

    _PYRO_EVENT_TIMEOUT = 0.001

    def __init__(self, service, multiplex):
        super(ServiceServerProcess, self).__init__(daemon=service.DAEMON,
                                            logging=service.LOGGING,
                                            thread=service.THREADING)
        self._service = service
        self._multiplex = multiplex

    def _serve(self):
        logger = self.get_logger(self._service.get_pyro_name() + "_PROCESS")
        if self._multiplex:
            logger.debug("Servertype: Multiplex")
            Pyro4.config.SERVERTYPE = "multiplex"
        else:
            logger.debug("Servertype: Threadpool")
        sys.excepthook = excepthook
        Pyro4.config.DOTTEDNAMES = True

        # we're using custom classes, so need to use pickle
        Pyro4.config.SERIALIZERS_ACCEPTED = set(['pickle'])

        logger.debug("Create service object")
        if self._multiplex and issubclass(self._service,
                                          CallbackService):
            logger.error("CallbackService can not be used in multiplex mode")
            self._queue.put(self.ERROR)
            return
        self._obj = self._service()
        logger.debug("Create pyro daemon")
        server = Pyro4.Daemon()
        logger.debug("Register service object at daemon")
        uri = server.register(self._obj)
        logger.debug("Register service uri at name server")
        with NameServer.locate() as ns:
            ns.register(self._service.get_pyro_name(), uri, safe=True)

        self._running = mp.Event()
        self._running.set()

        logger.debug("Create and start thread to stop the server")
        t = Thread(target=self._stop_thread, args=(server, ))
        t.daemon = True
        t.start()

        logger.debug("Create and start thread to initialize the resources")
        t = Thread(target=self._init_resources, args=(self._obj, ))
        t.start()
        try:
            self._request_loop(server, logger)
        except:
            logger.error("".join(Pyro4.util.getPyroTraceback()))

    def _request_loop(self, pyrodaemon, logger):
        logger.debug("Start Pyro4 request loop")
        try:
            # Pyro4 request loop
            while self._running.is_set():
                sockets = set(pyrodaemon.sockets)
                sockets, _, _ = select.select(sockets, [], [],
                                              self._PYRO_EVENT_TIMEOUT)

                if sockets:
                    logger.debug("Handle pyro events")
                    pyrodaemon.events(sockets)
                    logger.debug("Finished pyro events")
        except Pyro4.errors.ConnectionClosedError:
            logger.error("The connection was unexpectedly closed")
            raise
        except:
            logger.error("".join(Pyro4.util.getPyroTraceback()))
        finally:
            try:
                logger.debug("Unregister at nameserver")
                with NameServer.locate() as ns:
                    ns.remove(self._service.get_pyro_name())
            except NameServerError:
                pass  # Happens if name server has already shut down

            logger.debug("Close pyro daemon")
            try:
                # do not join the workers
                # may take long time
                pyrodaemon.transportServer.close(joinWorkers=False)
            except:
                # no threadpool server
                pyrodaemon.close()
            logger.debug("Finished request loop")

    def _init_resources(self, service):
        logger = self.get_logger(self._service.get_pyro_name() + "_PROCESS")

        logger.debug("Init service ressouces")
        try:
            service.init_resources()
        except:
            logger.error("".join(Pyro4.util.getPyroTraceback()))
            self._queue.put(self.ERROR)
        else:
            logger.debug("Put ready on the queue")
            self._queue.put(self.READY)

    def _stop_thread(self, server):
        while self._queue.get() != self.CLOSE:
            pass

        self._running.clear()


class QtServiceServerProcess(ServiceServerProcess):

    def _serve(self):
        try:
            from PyroMP.Qt import QtGui
        except ImportError as exc:
            logger = self.get_logger(self._service.get_pyro_name() + "_PROCESS")
            logger.error("ImportError: {}".format(exc.message))
            self._queue.put(self.ERROR)
        else:
            self._initialized = mp.Event()
            self._qt_gui = QtGui
            self._app = QtGui.QApplication([])  # @UndefinedVariable
            super(QtServiceServerProcess, self)._serve()

    def _anyQtWindowsAreOpen(self):
        return any(w.isVisible() for w in
                   self._qt_gui.QApplication.topLevelWidgets())

    def _init_resources(self, service):
        logger = self.get_logger(self._service.get_pyro_name() + "_PROCESS")

        logger.debug("Init service resources")
        try:
            service.init_resources()
        except:
            logger.error("".join(Pyro4.util.getPyroTraceback()))
            self._queue.put(self.ERROR)

        self._initialized.set()

    def _close_resources(self):
        logger = self.get_logger(self._service.get_pyro_name() + "_PROCESS")

        logger.debug("Close service resources")
        try:
            self._obj.close_resources()
        except:
            logger.error("".join(Pyro4.util.getPyroTraceback()))
            self._queue.put(self.ERROR)

        self._running.clear()

    def _request_loop(self, pyrodaemon, logger):
        run_qt_loop = False
        qt_windows_closed = False
        logger.debug("Start mixed request loop")
        try:
            while self._running.is_set():

                # Qt event loop
                # started when initialization has finished
                if run_qt_loop:
                    if not self._anyQtWindowsAreOpen():
                        logger.debug("All windows closed -> stop service")

                        # run close resources in another thread
                        # to avoid deadlocks
                        logger.debug("Create and start thread to close all resources")
                        t = Thread(target=self._close_resources)
                        t.start()

                        # disable Qt event loop
                        # prevent from restarting
                        run_qt_loop = False
                        qt_windows_closed = True

                    self._app.processEvents()
                    self._app.sendPostedEvents(None, 0)
                else:
                    if self._initialized.is_set() and not qt_windows_closed:

                        logger.debug("Run Qt main")
                        try:
                            self._obj.qt_main()
                        except:
                            logger.error("".join(Pyro4.util.getPyroTraceback()))
                            self._queue.put(self.ERROR)
                            break
                        else:
                            logger.debug("Put ready on the queue")
                            self._queue.put(self.READY)
                            run_qt_loop = True

                # Pyro4 request loop
                sockets = set(pyrodaemon.sockets)
                sockets, _, _ = select.select(sockets, [], [],
                                              self._PYRO_EVENT_TIMEOUT)

                if sockets:
                    logger.debug("Handle pyro events")
                    pyrodaemon.events(sockets)
                    logger.debug("Finished pyro events")
        except:
            logger.error("".join(Pyro4.util.getPyroTraceback()))
        finally:
            try:
                logger.debug("Unregister at nameserver")
                with NameServer.locate() as ns:
                    ns.remove(self._service.get_pyro_name())
            except NameServerError:
                pass  # Happens if name server has already shut down

            logger.debug("Close pyro daemon")
            try:
                # do not join the workers
                # may take long time
                pyrodaemon.transportServer.close(joinWorkers=False)
            except:
                # no threadpool server
                pyrodaemon.close()
            logger.debug("Finished request loop")


class ServiceProcessManager(object):

    _server = {}

    @classmethod
    def is_running(cls, service):
        ns = NameServer.locate()

        try:
            ns.lookup(service.get_pyro_name())
            return True
        except Pyro4.errors.NamingError:
            return False
        finally:
            ns._pyroRelease()

    @classmethod
    def start(cls, service, multiplex=False):
        if not cls.is_running(service):
            if issubclass(service, QtService):
                cls._server[service] = QtServiceServerProcess(service,
                                                              multiplex)
            else:
                cls._server[service] = ServiceServerProcess(service,
                                                            multiplex)
            cls._server[service].start()

    @classmethod
    def stop(cls, service):
        if cls.is_running(service) and service in cls._server:
            with service.get_connection(async=False) as conn:
                conn.close_resources()

            cls._server[service].stop()
            del(cls._server[service])

    @classmethod
    def stop_all(cls):
        keys = cls._server.keys()
        for service in keys:
            cls.stop(service)


# Avoid error due to circular import
import PyroMP.log_server as log
