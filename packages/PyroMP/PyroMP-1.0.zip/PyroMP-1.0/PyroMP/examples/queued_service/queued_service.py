#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
QUEUED SERVICE EXAMPLE
----------------------

How to implement an QueuedService and
how is the execution order influenced by the priorities?

The function are called in alternating order, but we expect:

- Slow operation
- Slow operation
- Slow operation
- Fast operation
- Fast operation
- Fast operation


.. created on 17.09.2013
.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-in
import time

# Internal
import PyroMP.log_server as log
from PyroMP import (NameServer,
                    priority,
                    QueuedService,
                    Service)


class TestService(Service):
    """"Service is wrapped by the QueuedService,
    that manages the order of execution"""

    @priority(5)
    def fast_operation(self):
        logger = self.get_logger()
        logger.info("Fast operation")
        time.sleep(1)
        return 1

    @priority(10)
    def slow_operation(self):
        logger = self.get_logger()
        logger.info("Slow operation")
        time.sleep(5)
        return 5


class QueuedTestService(QueuedService):

    CLASS = TestService


def main():
    with QueuedTestService() as service:
        logger = log.create_logger("MAIN")
        service.slow_operation()
        service.fast_operation()
        service.slow_operation()
        service.fast_operation()
        result1 = service.slow_operation()
        result2 = service.fast_operation()
        logger.info("All operations started")

        logger.info("Wait to finish all operations")
        service.sync.stop_listener()
        logger.info("Listener has stopped")

        logger.info("Result1 = {} (expect 5)".format(result1.value))
        logger.info("Result2 = {} (expect 1)".format(result2.value))


if __name__ == '__main__':
    with NameServer():
        with log.LogServer():
            log.set_loglevel(log.INFO)
            main()
