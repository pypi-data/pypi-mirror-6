#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
QUEUED CALLBACK EXAMPLE
-----------------------

Example implementation for callbacks with a QueuedService
to a CallbackObject

.. created on 17.09.2013

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-In
import time

# External

# Internal
import PyroMP.log_server as log
from PyroMP import (callback,
                    CallbackObject,
                    CallbackServer,
                    Event,
                    NameServer,
                    QueuedService,
                    Service)
from PyroMP.errors import ForbiddenAttributeAccessError


class FakeEvent(object):

    def register(self, obj):
        pass


class TestService(Service):

    def __init__(self, multiplex=False, async=True):
        super(TestService, self).__init__(multiplex, async)
        self.event = Event()

    def callback(self, callback):
        # call callback function directly
        callback.call("Callback test")

    def send_message(self, msg):
        # trigger event with argument
        self.event.trigger(msg)

    def trigger_event(self):
        self.event.trigger()


class QueuedTestService(QueuedService):

    CLASS = TestService


class LogObject(CallbackObject):
    """Object which receives the callbacks
    """

    def __init__(self, name):
        super(LogObject, self).__init__()
        self.name = name
        self.logger = log.create_logger(name)

    @callback
    def log(self, msg=None):
        self.logger.info("log(msg={!r})".format(msg))
        if msg is not None:
            self.logger.info(msg)


def main():
    logger = log.create_logger("MAIN")
    # Start CallbackServer for CallbackObjects
    with CallbackServer():
        with QueuedTestService() as service:
            callback1 = LogObject("Callback1")
            callback2 = LogObject("Callback2")

            # normal callback
            service.callback(callback1.log)

            # register for event
            service.event.register(callback1.log)
            service.event.register(callback2.log)

            # trigger event in different ways
            service.trigger_event()
            service.sync.send_message("Hallo Welt!")

            try:
                # events may not be triggered directly
                # in queued services
                service.sync.event.trigger()
                logger.error("ForbiddenAttributeAccessError was "
                             "NOT raised")
            except ForbiddenAttributeAccessError:
                logger.info("ForbiddenAttributeAccessError was "
                            "raised (as expected)")

            try:
                # only PyroMP.Event objects can be accessed
                # to register and unregister
                service.sync.fake_event.register(callback1.log)
                logger.error("ForbiddenAttributeAccessError was "
                             "NOT raised")
            except ForbiddenAttributeAccessError:
                logger.info("ForbiddenAttributeAccessError was "
                            "raised (as expected)")

            # callbacks are asynchronous
            # wait for them to be performed
            time.sleep(0.5)


if __name__ == '__main__':
    with NameServer():
        with log.LogServer():
            log.set_loglevel(log.INFO)
            main()
