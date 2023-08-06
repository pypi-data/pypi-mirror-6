#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
.. Created on 10.10.2013
.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
"""


from __future__ import print_function, unicode_literals, division


class PyroMPError(Exception):
    """Base class for all errors of this package"""
    pass


class CallbackServerAlreadyRunningError(PyroMPError):
    """Raised when the :class:`~PyroMP.CallbackServer`
    is already started"""
    pass


class CallbackServerNotRunningError(PyroMPError):
    """Raised when the :class:`~PyroMP.CallbackServer`
    has not been started"""
    pass


class ForbiddenAttributeAccessError(PyroMPError):
    """Raised when an attribute not of :class:`~PyroMP.Event` class or its
    :meth:`~PyroMP.Event.trigger` function is called of a
    :class:`~PyroMP.QueuedService` is accessed"""
    pass


class NameServerError(PyroMPError):
    """Raised when a :class:`~PyroMP.NameServer` was not found"""
    pass


class ServerError(PyroMPError):
    """Raised when an error occurred during starting an server process
    or thread"""
    pass


class ServiceAlreadyStoppedError(PyroMPError):
    """Raised when a function could not be executed because the
    :class:`~PyroMP.QueuedService` has already stopped"""
    pass


class ServiceNotAvailableError(PyroMPError):
    """Raised when trying to connect to a :class:`~PyroMP.Service`
    that is not running"""
    pass


class UnknownCommandError(PyroMPError):
    """Raised when an unknown command is on
    :class:`~PyroMP.QueuedService` command queue"""
    pass