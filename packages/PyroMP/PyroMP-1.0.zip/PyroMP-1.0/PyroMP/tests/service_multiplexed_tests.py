#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 10.10.2013

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-in
import unittest
import os

# Extern
from testfixtures import compare

# Intern
import PyroMP.log_server as log
from PyroMP import Service, NameServer
from PyroMP.errors import NameServerError


LOG_FILE = os.path.abspath("test.log")


class ObjectWrapper(object):

    def __init__(self, obj):
        self.obj = obj


class TestService(Service):

    def __init__(self, async=False):
        super(TestService, self).__init__(async=async,
                                          multiplex=True)
        self.logger = self.get_logger()
        with open(LOG_FILE, 'w'):
            pass  # clear file
        self.logger.add_filehandler(LOG_FILE, log.Formatter())

    def crash(self):
        self.logger.info("Divide by zero")
        _ = 5 / 0

    def calculate(self):
        self.logger.info("slow operation")
        return 50

    def boomerang(self, *args, **kwargs):
        return args, kwargs

    def return_self(self):
        return self

    def return_self_wrapped(self):
        return ObjectWrapper(self)


class AnotherTestService(Service):

    def __init__(self):
        super(AnotherTestService, self).__init__(async=False,
                                                 multiplex=False)

    def forward_call(self):
        with TestService.get_connection(async=False) as service:
            return service.calculate()


class ServiceAsLocalObjectTest(unittest.TestCase):

    def setUp(self):
        # stop already running LogServer
        try:
            log.LogServer.stop()
        except NameServerError:
            # no log server is running
            pass
        NameServer.stop()

        self.obj = TestService()

    def test_isRunning_NameServerError(self):
        with self.assertRaises(NameServerError):
            TestService.is_running()

    def test_argumentsPassed(self):
        ref_args = ("test1", "test2")
        ref_kwargs = {"kwarg1": 23}
        result = self.obj.boomerang(*ref_args,
                                    **ref_kwargs)
        self.assertEqual(result, (ref_args, ref_kwargs))

    def test_resultIsPassed(self):
        test_result = self.obj.calculate()
        compare(test_result, 50)

    def test_exceptionIsPassed(self):
        with self.assertRaises(ZeroDivisionError):
            self.obj.crash()


class ServiceTest(unittest.TestCase):

    def setUp(self):
        NameServer.start()
        log.LogServer.start()
        log.set_loglevel(log.DEBUG)

    def test_callFunction_noError(self):
        with TestService(async=False) as service:
            service.calculate()

    def test_isRunning_True(self):
        with TestService(async=False):
            self.assertTrue(TestService.is_running())

    def test_isRunning_False(self):
        self.assertFalse(TestService.is_running())

    def test_sync_argumentsPassed(self):
        with TestService(async=False) as service:
            ref_args = ("test1", "test2")
            ref_kwargs = {"kwarg1": 23}
            result = service.boomerang(*ref_args,
                                            **ref_kwargs)
            self.assertEqual(result, (ref_args, ref_kwargs))

    def test_async_argumentsPassed(self):
        with TestService(async=True) as service:
            ref_args = ("test1", "test2")
            ref_kwargs = {"kwarg1": 23}
            result = service.boomerang(*ref_args,
                                             **ref_kwargs)
            self.assertEqual(result.value, (ref_args, ref_kwargs))

    def test_sync_resultIsPassed(self):
        with TestService(async=False) as service:
            test_result = service.calculate()
            compare(test_result, 50)

    def test_callFromAnotherService_resultIsPassed(self):
        with TestService(async=False):
            with AnotherTestService() as service:
                test_result = service.forward_call()
                compare(test_result, 50)

    def test_async_resultIsPassed(self):
        with TestService(async=True) as service:
            test_result = service.calculate()
            compare(test_result.value, 50)

    def test_sync_exceptionIsPassed(self):
        with TestService(async=False) as service:
            with self.assertRaises(ZeroDivisionError):
                service.crash()

    def test_async_exceptionIsPassed(self):
        with TestService(async=True) as service:
            result = service.crash()
            with self.assertRaises(ZeroDivisionError):
                result.value

    # test autoproxy feature
    def test_selfReturned_isProxy(self):
        with TestService(async=False) as service:
            import Pyro4
            proxy = service.return_self()
            self.assertIsInstance(proxy, Pyro4.Proxy)

    # test autoproxy feature
    def test_WrappedSelfReturned_isProxy(self):
        with TestService(async=False) as service:
            import Pyro4
            wrapped = service.return_self_wrapped()
            self.assertIsInstance(wrapped.obj, Pyro4.Proxy)

