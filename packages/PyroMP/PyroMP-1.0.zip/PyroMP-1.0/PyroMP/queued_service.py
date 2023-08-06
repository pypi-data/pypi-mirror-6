#!/usr/bin/python
# -*- coding: utf-8 -*-

# Created on 17.09.2013
"""
.. currentmodule:: PyroMP

What means 'Queued'?
--------------------

'Queued' means the service stores the function calls in a
:class:`~multiprocessing.Queue` and the execution order
is according to their priorities.

Internally the commands are forwarded to a :class:`~Queue.PriorityQueue`,
which is not process safe.

Using a separate result queue the return values are passed to the according
callers.

.. image:: images/queued_service.png

How to define an object for queued access?
------------------------------------------

A :class:`QueuedService` wraps a normal :class:`Service`.
The :obj:`priority` decorator is used to define priorities for the functions.
Higher priorities lead to earlier execution.
The default priority for not decorated functions is 0.

**Example:**

.. code-block:: python

    class ExampleService(object):

        @priority(5)
        def fast_operation(self):
            # do fast stuff

        @priority(10)
        def slow_operation(self):
            # do slow stuff

The following call sequence:

.. code-block:: python

    service.slow_operation()
    service.fast_operation()
    service.slow_operation()
    service.fast_operation()
    service.slow_operation()
    service.fast_operation()

leads to an execution order of:

#. ``slow_operation``
#. ``slow_operation``
#. ``slow_operation``
#. ``fast_operation``
#. ``fast_operation``
#. ``fast_operation``


How to define a Queued Service?
-------------------------------

Derive a class from :class:`QueuedService` and add a ``CLASS``
property, which contains the class of the object to be wrapped.

Example:

.. code-block:: python

    class QueuedExampleService(QueuedService):

        CLASS = TestObject

.. note::
    :func:`~Service.init_resources` and
    :func:`~Service.close_resources` are called on
    initialization and closing if provided by the wrapped object

.. note::
    For an extensive example see :ref:`queued_service_example`.

Callbacks and Events
--------------------

Using callbacks does not differ from the normal use, but using
:class:`Events <Event>` does.
It works to :func:`~Event.register` and :func:`~Event.unregister`
as usual, but it is not possible to call :func:`~Event.trigger`
remotely. This will cause a
:class:`~PyroMP.errors.ForbiddenAttributeAccessError` to be raised.
(See :ref:`queued_callback_example`)

.. warning:: It is not possible to wrap a :class:`CallbackObject` or
             :class:`CallbackService` or a subclass of them by a
             :class:`QueuedService`!

Autoproxy
---------

The :ref:`autoproxy` feature is implemented for :class:`QueuedService`, too.
If an object that is wrapped by the :class:`QueuedService` is passed to another process.
It is replaced by a :class:`~Pyro4.core.Proxy` to the :class:`QueuedService`

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
"""

from __future__ import print_function, unicode_literals, division

# Built-in
import sys
import uuid
import multiprocessing as mp
import functools

# Extern
import Pyro4
import six
from six.moves import queue
from six.moves import copyreg

# Intern
from . import log_server as log
from PyroMP.service import Service
from PyroMP.server import ServerProcess
from PyroMP.callback import Event, CallbackObject, CallbackService
from PyroMP.errors import (ForbiddenAttributeAccessError,
                           ServiceAlreadyStoppedError,
                           UnknownCommandError)


def register_proxy_replacer(object_type, uri):
    """Registers a function that pickle will use to replace
    objects of the given type by a proxy to the given uri

    Adapted from Pyro4 autoproxy feature
    """

    def obj_to_proxy(obj):
        return Pyro4.Proxy(uri).__reduce__()

    try:
        copyreg.pickle(object_type, obj_to_proxy)
    except TypeError:
        pass


def priority(prio):
    def temp(func):
        """Marks class method as callback function
        """
        setattr(func, "_queue_priority", prio)
        return func
    return temp


class _IDQueue(object):

    def __init__(self):
        self._queue = mp.Queue()

    def empty(self):
        return self._queue.empty()

    def get(self, id_):
        obj = self._queue.get()
        while obj[0] != id_:
            self._queue.put(obj)
            obj = self._queue.get()

        return obj[1]

    def put(self, id_, value):
        self._queue.put((id_, value))


@functools.total_ordering
class _QueuedCommand(object):

    def __init__(self, func_name, priority, args, kwargs):
        if priority is None:
            raise AttributeError(func_name)

        self._func_name = func_name
        self._priority = priority
        self._id = uuid.uuid4().hex
        self._args = args
        self._kwargs = kwargs

    @property
    def func_name(self):
        return self._func_name

    def execute(self, obj, result_queue):
        func = getattr(obj, self._func_name)
        try:
            value = func(*self._args, **self._kwargs)
        except Exception as exc:
            value = exc
        result_queue.put(self._id, value)

    def not_executed(self, result_queue):
        result_queue.put(self._id, ServiceAlreadyStoppedError())

    def get_result(self, result_queue):
        return result_queue.get(self._id)

    def __eq__(self, other):
        """Return self == other"""
        return other._priority == self._priority

    def __lt__(self, other):
        """Return self < other"""
        return other._priority < self._priority

    def __str__(self):
        if six.PY3:
            return self.__unicode__()
        else:
            return unicode(self).encode('utf-8')

    def __unicode__(self):
        return "<Command({}, {}, {}, {!r}, {!r})>".format(
                    self._func_name, self._priority, self._id,
                    self._args, self._kwargs)

    def __repr__(self):
        return six.text_type(self)


class _EventCommand(_QueuedCommand):

    def __init__(self, name, attr, args, kwargs):
        priority = sys.float_info.max
        super(_EventCommand, self).__init__(attr, priority, args, kwargs)
        self._event_name = name

    def execute(self, obj, result_queue):
        event = getattr(obj, self._event_name)
        if isinstance(event, Event):
            super(_EventCommand, self).execute(event, result_queue)
        else:
            result_queue.put(self._id,
                             ForbiddenAttributeAccessError("Only events are accessible"))

    def __unicode__(self):
        return "<_EventCommand({}, {}, {}, {!r}, {!r})>".format(
                    self._event_name, self._func_name, self._id,
                    self._args, self._kwargs)


class _QueueListener(ServerProcess):

    FINISH_AND_STOP = "finish and stop"

    def __init__(self, class_, uri, result_queue):
        super(_QueueListener, self).__init__(daemon=True,
                                            logging=True,
                                            thread=False)
        self.logger = log.create_logger("QueueListener_local")

        self._class = class_
        self._uri = uri
        self._result_queue = result_queue
        self._obj = None
        self._priority_queue = None
        self._stop_when_finished = False

    def finish_and_stop(self):
        self.logger.debug("Send 'finish_and_stop'")
        self._queue.put(self.FINISH_AND_STOP)
        self.join()

    def join(self):
        super(_QueueListener, self).join()
        self._flush(self._queue)

    def send_command(self, command):
        if self.running():
            self.logger.debug("Send '{}'".format(command))
            self._queue.put(command)
        else:
            self.logger.error("Process has stopped: Can't"
                              " execute '{}'".format(command))
            raise ServiceAlreadyStoppedError()

    def _priority_queue_is_empty(self):
        if self._priority_queue is None:
            return True
        else:
            return self._priority_queue.empty()

    def _flush(self, q):
        """Pops  all outstanding commands from queue ``q``
        and marks them as not executed.
        """
        while q:
            try:
                command = q.get_nowait()
                if isinstance(command, _QueuedCommand):
                    self.logger.error("Invalidate '{}'".format(command))
                    command.not_executed(self._result_queue)
            except queue.Empty:
                break

    def _receive_commands(self):
        """Returns 'False' when the process has to stop
        """
        if self._priority_queue_is_empty():
            if self._stop_when_finished:
                return False
            else:
                # nothing else to do
                # so block until a new command comes in
                self.logger.debug("Wait for incoming commands")
                commands = [self._queue.get()]
        else:
            # init commands list
            # will be filled next
            commands = []

        while not self._queue.empty():
            try:
                commands.append(self._queue.get_nowait())
            except queue.Empty:
                break

        stop_process = False
        for command in commands:
            self.logger.debug("Received: {}".format(repr(command)))
            if isinstance(command, _QueuedCommand):
                self.logger.debug("Put: {}".format(repr(command)))
                self._priority_queue.put(command)
            elif command == self.FINISH_AND_STOP:
                self._stop_when_finished = True
            elif command == self.CLOSE:
                stop_process = True
            else:
                raise UnknownCommandError(repr(command))

        return not stop_process

    def _serve(self):
        self.logger = log.create_logger("QueueListener_process")
        self._obj = self._class()

        # if object has init_resources function
        # it has to be executed
        try:
            init = self._obj.init_resources
        except AttributeError:
            pass
        else:
            try:
                init()
            except:
                self.logger.error("".join(Pyro4.util.getPyroTraceback()))
                self._queue.put(self.ERROR)
                return

        register_proxy_replacer(self._class, self._uri)
        self.logger.debug("Put ready on the queue")
        self._queue.put(self.READY)
        self._priority_queue = queue.PriorityQueue()
        try:
            while self._receive_commands():
                self.logger.debug("Get next command")
                command = self._priority_queue.get_nowait()
                self.logger.debug("Call '{}'".format(command))
                command.execute(self._obj, self._result_queue)
        except:
            self.logger.error("".join(Pyro4.util.getPyroTraceback()))

        self._flush(self._priority_queue)

        # if object has close_resources function
        # it has to be executed
        try:
            close = self._obj.close_resources
        except AttributeError:
            pass
        else:
            try:
                close()
            except:
                self.logger.error("".join(Pyro4.util.getPyroTraceback()))
                self._queue.put(self.ERROR)
                return


class _FunctionWrapper(object):

    def __init__(self, name, priority, _callable):
        self._callable = _callable
        self._priority = priority
        self._name = name
        self._attribute = None

    def __getattr__(self, name):
        if (self._attribute is None and
            name in ("register", "unregister")):
            self._attribute = name
            return self
        elif (self._attribute is None and
              name in ("trigger")):
            raise ForbiddenAttributeAccessError()
        else:
            raise AttributeError()

    def __call__(self, *args, **kwargs):
        logger = log.create_logger("FunctionWrapper({})".format(self._name))
        logger.debug("Create command")
        if self._attribute is None:
            command = _QueuedCommand(self._name, self._priority, args, kwargs)
        else:
            command = _EventCommand(self._name, self._attribute, args, kwargs)

        logger.debug("Forward command: {!r}".format(command))
        return self._callable(command)


class QueuedService(Service):
    """Bases: :class:`Service`

    Manages the whole queuing stuff for queued calls.
    """

    _own_attributes = ("close_resources",
                       "stop_listener",
                       "stop_listener_nowait")

    DAEMON = False
    CLASS = None

    def __init__(self, async=True):
        self.assert_class(self.CLASS)
        multiplex = False
        super(QueuedService, self).__init__(multiplex, async)
        self._queue_listener = None
        self._result_queue = None
        self.__class = self.CLASS
        self._logger = log.create_logger("QueuedService")

    def assert_class(self, class_):
        if issubclass(class_, CallbackObject):
            raise TypeError("'CLASS' must not be a subclass of 'CallbackObject'")
        if issubclass(class_, CallbackService):
            raise TypeError("'CLASS' must not be a subclass of 'CallbackService'")

    def init_resources(self):
        super(QueuedService, self).init_resources()
        self._result_queue = _IDQueue()
        daemon = self._pyroDaemon
        uri = daemon.uriFor(self)
        self._queue_listener = _QueueListener(self.__class,
                                              uri,
                                              self._result_queue)
        self._queue_listener.start()

    def __getattr__(self, name):
        self._logger.debug("__getattr__: {}".format(name))

        if name in self._own_attributes or name.startswith("_"):
            self._logger.debug("Own attribute")
            raise AttributeError(name)

        else:
            self._logger.debug("Return queued call")
            if name in self.__class._PRIORITY_DICT:
                priority = self.__class._PRIORITY_DICT[name]
            else:
                # maybe an event call
                # so priority will not be necessary
                priority = None
            self._logger.debug("Create function wrapper")
            wrapper = _FunctionWrapper(name, priority, self._queued_call)
            self._logger.debug("Return function wrapper")
            return wrapper

    def close_resources(self):
        """Stop the queue listener

        Called before stopping the queued service process
        """
        self.stop_listener_nowait()

    def _queued_call(self, command):
        self._logger.debug("Call '{!r}'".format(command))
        self._queue_listener.send_command(command)
        result = command.get_result(self._result_queue)
        if isinstance(result, Exception):
            raise result
        else:
            return result

    # FIXME: naming not intuitive
    def stop_listener(self):
        self._logger.debug("Execute 'stop_listener()'")
        if self._queue_listener.running():
            self._logger.debug("Listener still running -> finish_and_stop()")
            self._queue_listener.finish_and_stop()

    def stop_listener_nowait(self):
        self._logger.debug("Execute 'stop_listener_nowait()'")
        if self._queue_listener.running():
            self._logger.debug("Listener still running -> stop()")
            self._queue_listener.stop()
