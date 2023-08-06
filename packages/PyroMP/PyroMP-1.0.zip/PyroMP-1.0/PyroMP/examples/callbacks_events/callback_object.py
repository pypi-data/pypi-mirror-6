#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
CALLBACK OBJECT EXAMPLE
-----------------------

Example implementation for callbacks to the main thread
using a CallbackObject and a normal Service


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
                    Service)


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
    with TestService(async=False) as service:
        # Start CallbackServer for CallbackObjects
        with CallbackServer():
            callback1 = LogObject("Callback1")
            callback2 = LogObject("Callback2")

            # normal callback
            service.callback(callback1.log)

            # normal function call
            callback1.log()
            callback2.log()

            # register for event
            service.event.register(callback1.log)
            service.event.register(callback2.log)

            # trigger event in different ways
            service.trigger_event()
            service.event.trigger("Direct triggered")
            service.send_message("Hallo Welt!")

            # callbacks are asynchronous
            # wait for them to be performed
            time.sleep(0.5)


if __name__ == '__main__':
    with NameServer():
        with log.LogServer():
            log.set_loglevel("INFO")
            main()

