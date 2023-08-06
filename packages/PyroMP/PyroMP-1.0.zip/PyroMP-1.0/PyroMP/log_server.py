#!/usr/bin/python
# -*- coding: utf-8 -*-

# Created on 03.09.2013
'''
.. _logging:

Logging
-------

The ``PyroMP`` package has a module to provide logging supporting
the multiprocessing feature.
The basic idea is to have one :class:`~PyroMP.Service` named :class:`LogServer`
which manages several :class:`logging.Logger`.
The PyroMP logger acts like the built-in one but forwards everything to
the logger with the same name at the :class:`LogServer`.

Usually it is used with a concurrent :class:`LogServer`:

.. code-block:: python

    from PyroMP import NameServer
    import PyroMP.log_server as log
    with NameServer():
        with log.LogServer():
            log.set_loglevel(log.INFO)
            logger = log.create_logger("ExampleLogger")
            logger.info("Example message")

Log:

.. runblock:: pycon
    :hidden-statements: 1 2

    >>> from PyroMP import NameServer
    >>> NameServer.stop()
    >>> import PyroMP.log_server as log
    >>> NameServer.disable()
    >>> log.set_loglevel(log.INFO)
    >>> logger = log.create_logger("ExampleLogger")
    >>> logger.info("Example message")




but it can also be used locally:

.. code-block:: python

    from PyroMP import NameServer
    import PyroMP.log_server as log
    # disable NameServer to avoid unexpected behavior
    # in case that another NameServer is running concurrently
    NameServer.disable()
    log.set_loglevel(log.INFO)
    logger = log.create_logger("ExampleLogger")
    logger.info("Example message")

Log:

.. runblock:: pycon
    :hidden-statements: 1 2

    >>> from PyroMP import NameServer
    >>> NameServer.stop()
    >>> import PyroMP.log_server as log
    >>> NameServer.disable()
    >>> log.set_loglevel(log.INFO)
    >>> logger = log.create_logger("ExampleLogger")
    >>> logger.info("Example message")


As you can see, ``PyroMP.log_server`` module exports the log levels
as exported by :mod:`logging` (see
`Python Documentation <http://docs.python.org/2/howto/logging.html#logging-basic-tutorial>`_):

- INFO
- DEBUG
- WARNING
- ERROR
- CRITICAL
- FATAL
- NOTSET

The same is applied for :class:`logging.Formatter` which is
available using ``PyroMP.log_server.Formatter``

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-in
import logging
import functools
from copy import copy

# Intern
from .service import Service


# Export log levels
INFO = logging.INFO
DEBUG = logging.DEBUG
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
NOTSET = logging.NOTSET


# Export Formatter
Formatter = logging.Formatter

MAX_LOGGER_NAME_LEN = 20  # adjust NUM_START_LETTERS appropriately
NUM_START_LETTERS = 7
LOGSERVER_PREFIX = "LogServer"

_local_server = None


def _start_local():
    global _local_server
    if _local_server is None:
        _local_server = LogServer()
        _local_server.init_resources()


def create_logger(name):
    """Factory function, that returns a
    proxy for a :class:`logging.Logger`.

    If a :class:`LogServer` is running, it is used.
    Else a local :class:`logging.Logger` is used.

    The returned object supports all functions
    that are provided by :class:`logging.Logger`
    """
    if LogServer.is_running():
        return LoggerProxy(name)
    else:
        _start_local()
        return LocalLoggerProxy(name)


def set_loglevel(level):
    """Set the level to ``level`` for all existing loggers.

    Parameters
    ----------
    level : int
        Desired level

    See Also
    --------
    logging.Logger.setLevel
    """
    if LogServer.is_running():
        with LogServer.get_connection(async=False) as log_service:
            log_service.set_loglevel(level)
    else:
        _start_local()
        global _local_server
        _local_server.set_loglevel(level)


def get_server_root_logger():
    """
    Returns
    -------
    root_logger : LoggerProxy
        Logger proxy to the root logger of the current :class:`LogServer`
    """
    return create_logger("")


class LoggerProxy(object):
    """Proxy for a :class:`logging.Logger`
    at the :class:`LogServer`

    Supports all functions that are provided by :class:`logging.Logger`
    """

    def __init__(self, name):
        """
        Parameters
        ----------
        name : unicode
            Name of the logger

        Notes
        -----
        The output format of the logger is:

        ``YYYY-MM-DD HH:MM:SS,MS - LoggerName - LEVEL - MESSAGE``
        """
        if len(name) > MAX_LOGGER_NAME_LEN:
            num_end_letters = MAX_LOGGER_NAME_LEN - NUM_START_LETTERS - 2
            self._name = (name[:NUM_START_LETTERS] + ".." +
                          name[- num_end_letters:])
        else:
            self._name = name
        self._create_logger()

    def _create_logger(self):
        with LogServer.get_connection(async=False) as log_service:
            log_service.create_logger(self._name)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError()
        else:
            return functools.partial(self._send_request, name)

    def _send_request(self, func_name, *args, **kwargs):
        with LogServer.get_connection(async=False) as log_service:
            func = getattr(log_service, func_name)
            func(self._name, *args, **kwargs)


class LocalLoggerProxy(LoggerProxy):
    """Proxy for a :class:`logging.Logger`
    at a local :class:`LogServer` object

    Supports all functions that are provided by :class:`logging.Logger`
    """

    def _create_logger(self):
        global _local_server
        _local_server.create_logger(self._name)

    def _send_request(self, func_name, *args, **kwargs):
        global _local_server
        func = getattr(_local_server, func_name)
        func(self._name, *args, **kwargs)


class LogServer(Service):
    """Bases: :class:`~PyroMP.Service`

    Service that manages the logging stuff,
    started in a thread.
    """

    LOGGING = False
    THREADING = True

    _own_attributes = ("create_logger",
                       "set_loglevel",
                       "add_filehandler",
                       "add_streamhandler")

    def __init__(self):
        super(LogServer, self).__init__(multiplex=True,
                                        async=False)

    def init_resources(self):
        self._logger = {}

        logger_name_length = MAX_LOGGER_NAME_LEN + len(LOGSERVER_PREFIX) + 1
        self._standard_formatter = logging.Formatter(("%(asctime)s - %(name)-{}s - "
                                                      "%(levelname)-8s - %(message)s")
                                                     .format(logger_name_length))

        self._root_logger = logging.getLogger(LOGSERVER_PREFIX)
        self._clear_handler(self._root_logger)
        self._root_logger.setLevel(NOTSET)
        self._logger[""] = self._root_logger

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_standard_formatter())
        self._root_logger.addHandler(console_handler)

    def __getattr__(self, name):
        if name in self._own_attributes or name.startswith("_"):
            raise AttributeError()

        return functools.partial(self._handle_request, name)

    def __getitem__(self, name):
        return self._logger[name]

    def _clear_handler(self, logger):
        # Clear all handlers
        if logger.handlers:
            for handler in logger.handlers:
                logger.removeHandler(handler)

    def _handle_request(self, func_name, logger_name, *args, **kwargs):
        func = getattr(self._logger[logger_name], func_name)
        return func(*args, **kwargs)

    def _get_standard_formatter(self):
        return copy(self._standard_formatter)

    def create_logger(self, logger_name):
        """Create new logger with standard stream handler"""

        if logger_name in self._logger:
            pass
        else:
            logger = self._root_logger.getChild(logger_name)

            self._clear_handler(logger)

            # Store logger
            self._logger[logger_name] = logger

    def remove(self, logger_name):
        try:
            del(self._logger[logger_name])
        except KeyError:
            pass

    def add_filehandler(self, logger_name, filename, formatter=None,
                        level=None):
        logger = self._logger[logger_name]

        # Add file handler
        file_handler = logging.FileHandler(filename, "a", "utf-8")
        if formatter is None:
            formatter = self._get_standard_formatter()

        if level:
            file_handler.setLevel(level)

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    def add_streamhandler(self, logger_name, stream=None, formatter=None,
                          level=None):
        logger = self._logger[logger_name]

        # Add file handler
        stream_handler = logging.StreamHandler(stream)
        if formatter is None:
            formatter = self._get_standard_formatter()

        if level:
            stream_handler.setLevel(level)

        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    def set_loglevel(self, level):
        """Set log level for server root logger"""
        self._root_logger.setLevel(level)

    @classmethod
    def is_running(cls):
        """Returns ``True`` if a LogServer is available otherwise ``False``
        """
        try:
            conn = cls.get_connection()
            conn.connect()
            conn.disconnect()
            return True
        except:
            return False
