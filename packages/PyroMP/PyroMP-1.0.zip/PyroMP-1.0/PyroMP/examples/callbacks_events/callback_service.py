#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
CALLBACK SERVICE EXAMPLE
------------------------

Example implementation for callbacks to another service
using a CallbackService and a normal Service


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
                    CallbackService,
                    Event,
                    NameServer,
                    Service)


class TestService(Service):

    def __init__(self, multiplex=False, async=True):
        super(TestService, self).__init__(multiplex, async)
        self.event = Event()

    def send_message(self, msg):
        # trigger event with argument
        self.event.trigger(msg)

    def trigger_event(self):
        self.event.trigger()


class LogService(CallbackService):
    """Service which receives the callbacks
    """

    def init_resources(self):
        super(LogService, self).init_resources()
        # register for event
        with TestService(async=False) as service:
            service.event.register(self.log)

    def close_resources(self):
        super(LogService, self).close_resources()
        # unregister for event
        with TestService(async=False) as service:
            service.event.unregister(self.log)

    @callback
    def log(self, msg=None):
        logger = self.get_logger()
        logger.info("log(msg={!r})".format(msg))
        if msg is not None:
            logger.info(msg)


def main():
    with TestService(async=False) as service:
        with LogService():
            # trigger event in different ways
            service.trigger_event()
            service.event.trigger("Direct triggered")
            service.send_message("Hallo Welt!")

            # callbacks are asynchronous
            # wait for them to be performed
            time.sleep(0.5)


if __name__ == '__main__':
    with NameServer(), log.LogServer():
        log.set_loglevel(log.INFO)
        main()
