#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 17.09.2013

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-in
import unittest
import os
import time

# Extern
from testfixtures import compare

# Intern
import PyroMP.log_server as log
from PyroMP.service import Service
from PyroMP.server import NameServer
from PyroMP.callback import CallbackObject, CallbackService
from PyroMP.queued_service import (priority,
                                   QueuedService,
                                   ServiceAlreadyStoppedError)

LOG_FILE = os.path.abspath("test.log")
TEST_LOGGER_NAME = "TestObject"


class ObjectWrapper(object):

    def __init__(self, obj):
        self.obj = obj


class TestService(Service):

    def __init__(self):
        self.logger = log.create_logger(TEST_LOGGER_NAME)
        with open(LOG_FILE, 'w'):
            pass  # clear file
        self.logger.add_filehandler(LOG_FILE, log.Formatter())

    def crash(self):
        self.logger.info("Divide by zero")
        _ = 5 / 0

    @priority(5)
    def fast_operation(self):
        self.logger.info("fast operation")
        time.sleep(0.1)
        return "fast"

    @priority(10)
    def slow_operation(self):
        self.logger.info("slow operation")
        time.sleep(1)
        return "slow"

    def boomerang(self, *args, **kwargs):
        return args, kwargs

    def return_self(self):
        return self

    def return_self_wrapped(self):
        return ObjectWrapper(self)


class QueuedTestService(QueuedService):

    CLASS = TestService


class QueuedCallbackObject(QueuedService):

    CLASS = CallbackObject


class QueuedCallbackService(QueuedService):

    CLASS = CallbackService


class CallbackObjectTest(unittest.TestCase):

    def setUp(self):
        NameServer.start()
        log.LogServer.start()
        log.set_loglevel(log.DEBUG)

    def test_CallbackObject_TypeError(self):
        with self.assertRaises(TypeError):
            QueuedCallbackObject()

    def test_CallbackService_TypeError(self):
        with self.assertRaises(TypeError):
            QueuedCallbackService()


class QueuedServiceTest(unittest.TestCase):

    def setUp(self):
        NameServer.start()
        log.LogServer.start()
        log.create_logger(TEST_LOGGER_NAME)
        log.set_loglevel(log.DEBUG)

        QueuedTestService.start()
        self.service = QueuedTestService.get_connection()
        self.service.connect()
        self.results = []

    def tearDown(self):
        logger = log.create_logger(TEST_LOGGER_NAME)
        logger.remove()

        self.service.disconnect()
        QueuedTestService.stop()

        # LogServer and NameServer are not stopped to save time
        # they are stopped automatically
        # when all tests are finished

    def read_log(self):
        with open(LOG_FILE) as f:
            return f.read()

    def slow_operation(self):
        r = self.service.slow_operation()
        self.results.append(r)
        return r

    def fast_operation(self):
        r = self.service.fast_operation()
        self.results.append(r)
        return r

    def check_results(self):
        # check for errors
        # exception will be raised when accessing value
        for r in self.results:
            r.value

    def test_callFunction_noError(self):
        self.service.sync.fast_operation()

    def test_correctCallSequence(self):
        self.slow_operation()
        # wait otherwise fast_opeation command
        # could reach the service too early
        time.sleep(0.5)
        self.fast_operation()
        self.slow_operation()
        self.fast_operation()
        self.slow_operation()
        # synchronous call to make sure
        # that everything has finished afterwards
        self.service.sync.fast_operation()

        self.check_results()

        reference_log = """slow operation
slow operation
slow operation
fast operation
fast operation
fast operation
"""
        compare(self.read_log(), reference_log)

    def test_argumentsPassed(self):
        ref_args = ("test1", "test2")
        ref_kwargs = {"kwarg1": 23}
        result = self.service.sync.boomerang(*ref_args,
                                             **ref_kwargs)
        self.assertEqual(result, (ref_args, ref_kwargs))

    def test_resultIsPassed(self):
        test_result = self.service.sync.slow_operation()
        compare(test_result, "slow")

    def test_exceptionIsPassed(self):
        with self.assertRaises(ZeroDivisionError):
            self.service.sync.crash()

    def test_functionNotCalled_ServiceAlreadyStoppedError(self):
        result1 = self.slow_operation()
        result2 = self.fast_operation()
        time.sleep(1)
        self.service.sync.stop_listener_nowait()
        result1.value
        with self.assertRaises(ServiceAlreadyStoppedError):
            result2.value

    def test_listenerHasStopped_ServiceAlreadyStoppedError(self):
        self.service.sync.stop_listener_nowait()
        result2 = self.fast_operation()

        with self.assertRaises(ServiceAlreadyStoppedError):
            result2.value

    def test_selfReturned_isProxy(self):
        import Pyro4
        proxy = self.service.sync.return_self()
        self.assertIsInstance(proxy, Pyro4.Proxy)

    def test_wrappedSelfReturned_isProxy(self):
        import Pyro4
        wrapped = self.service.sync.return_self_wrapped()
        self.assertIsInstance(wrapped.obj, Pyro4.Proxy)

TEST_FILE = os.path.abspath("test.txt")


class TestInitCloseRessourcesService(Service):

    def __init__(self, **kwargs):
        super(TestInitCloseRessourcesService, self).__init__(**kwargs)

    def close_resources(self):
        super(TestInitCloseRessourcesService, self).close_resources()
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    def init_resources(self):
        super(TestInitCloseRessourcesService, self).init_resources()
        with open(TEST_FILE, mode='w'):
            pass

    def initialized(self):
        return self._init

    def closed(self):
        return self._closed


class QueuedInitCloseRessourcesService(QueuedService):

    CLASS = TestInitCloseRessourcesService


class NormalServiceInitCloseTests(unittest.TestCase):
    """Tests to assert correct behavior of the test service
    """

    SERVICE_UNDER_TEST = TestInitCloseRessourcesService

    def setUp(self):
        if self.test_file_exists():
            os.remove(TEST_FILE)
        NameServer.start()
        log.LogServer.start()
        log.create_logger(TEST_LOGGER_NAME)
        log.set_loglevel(log.DEBUG)

    def tearDown(self):
        logger = log.create_logger(TEST_LOGGER_NAME)
        logger.remove()

    def test_file_exists(self):
        return os.path.exists(TEST_FILE)

    def test_testFile_doesNotExists(self):
        self.assertFalse(self.test_file_exists())

    def test_initialized_fileExists(self):
        with self.SERVICE_UNDER_TEST():
            self.assertTrue(self.test_file_exists())

    def test_closed_fileDoesntExists(self):
        with self.SERVICE_UNDER_TEST():
            pass
        self.assertFalse(self.test_file_exists())


class QueuedServiceInitCloseTests(NormalServiceInitCloseTests):

    SERVICE_UNDER_TEST = QueuedInitCloseRessourcesService
