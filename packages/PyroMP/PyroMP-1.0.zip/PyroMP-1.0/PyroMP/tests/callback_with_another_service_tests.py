#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 26.09.2013

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-in
import unittest
import time

# Extern
from testfixtures import LogCapture

# Intern
import PyroMP.log_server as log
from PyroMP.server import NameServer
from PyroMP.service import Service
from PyroMP.callback import (callback,
                             CallbackService,
                             Event)
from PyroMP.errors import ServerError


class MockService(CallbackService):

    def __init__(self):
        super(MockService, self).__init__(async=False)
        self._called = False
        self._arg = None

    def arg(self):
        return self._arg

    def called(self):
        return self._called

    def perform_callback(self, arg=None):
        with TestService() as service:
            service.callback(self.callback_function, arg)

    def perform_callback_with_kwarg(self, **kwargs):
        with TestService() as service:
            service.callback_with_kwargs(self.callback_function, **kwargs)

    def register(self):
        with TestService() as service:
            logger = self.get_logger()
            logger.debug("Register {!r}".format(self.callback_function))
            service.event.register(self.callback_function)

    def unregister(self):
        with TestService() as service:
            service.event.unregister(self.callback_function)

    @callback
    def callback_function(self, arg=None):
        self._called = True
        self._arg = arg

    @callback
    def error_callback(self, arg=None):
        self._called = True
        return 1 / 0


class MockServiceAutoregister(MockService):

    def init_resources(self):
        super(MockServiceAutoregister, self).init_resources()
        self.register()


class MockServiceAutoregisterError(MockService):

    def init_resources(self):
        super(MockServiceAutoregisterError, self).init_resources()
        with TestService() as service:
            logger = self.get_logger()
            logger.debug("Register {!r}".format(self.error_callback))
            service.event.register(self.error_callback)


class MockServiceAutoregisterError2(MockServiceAutoregisterError):
    pass


class TestService(Service):

    def __init__(self, multiplex=True, async=False):
        super(TestService, self).__init__(multiplex, async)
        self.event = Event()

    def __getattr__(self, name):
        self.get_logger().debug("getattr: {!r}".format(name))
        super(TestService, self).__getattr__(name)

    def callback(self, callback, arg=None):
        callback.call(arg)

    def callback_with_kwargs(self, callback, **kwargs):
        callback.call(**kwargs)

    def send_message(self, arg):
        self.event.trigger(arg)

    def send_message_with_kwarg(self, kwarg):
        self.event.trigger(arg=kwarg)

    def trigger_event(self):
        self.event.trigger()


class EventTests(unittest.TestCase):

    def setUp(self):
        NameServer.start()
        log.LogServer.start()
        log.set_loglevel(log.DEBUG)

    def test_TriggerAfterUnregister_CallbackNotCalled(self):
        with TestService() as service:
            with MockService() as test_obj:
                test_obj.register()
                test_obj.unregister()
                service.event.trigger()
                self.assertFalse(test_obj.called())

    def test_TriggerAfterUnregister_Autoregister_CallbackNotCalled(self):
        with TestService() as service:
            with MockServiceAutoregister() as test_obj:
                test_obj.unregister()
                service.event.trigger()
                self.assertFalse(test_obj.called())

    def test_trigger_CallbackCalled(self):
        with TestService() as service:
            with MockService() as test_obj:
                test_obj.register()
                service.event.trigger()
                time.sleep(1)  # wait for the callbacks
                self.assertTrue(test_obj.called())

    def test_TriggerAfterAutoregister_CallbackCalled(self):
        with TestService() as service:
            with MockServiceAutoregister() as test_obj:
                service.trigger_event()
                time.sleep(1)  # wait for the callbacks
                self.assertTrue(test_obj.called())

    def test_TriggerWithArg_CallbackCalled(self):
        with TestService() as service:
            with MockService() as test_obj:
                test_obj.register()
                service.event.trigger("Test")
                time.sleep(1)  # wait for the callbacks
                self.assertEqual(test_obj.arg(), "Test")

    def test_TriggerWithArgAfterAutoregister_CallbackCalled(self):
        with TestService() as service:
            with MockServiceAutoregister() as test_obj:
                service.send_message("Test")
                time.sleep(1)  # wait for the callbacks
                self.assertEqual(test_obj.arg(), "Test")

    def test_TriggerWithKwarg_CallbackCalled(self):
        with TestService() as service:
            with MockService() as test_obj:
                test_obj.register()
                service.event.trigger(arg="Test")
                time.sleep(1)  # wait for the callbacks
                self.assertEqual(test_obj.arg(), "Test")

    def test_TriggerWithKwargAfterAutoregister_CallbackCalled(self):
        with TestService() as service:
            with MockServiceAutoregister() as test_obj:
                service.send_message_with_kwarg("Test")
                time.sleep(1)  # wait for the callbacks
                self.assertEqual(test_obj.arg(), "Test")

    def test_triggerWithErrors_allCallbacksCalled(self):
        with TestService() as service:
            with MockServiceAutoregisterError() as test_obj1:
                with MockServiceAutoregisterError2() as test_obj2:
                    service.event.trigger()
                    time.sleep(1)  # wait for the callbacks
                    called_tuple = (test_obj1.called(),
                                    test_obj2.called())
                    self.assertEqual(called_tuple, (True, True))

    def test_triggerWithErrors_errorsLogged(self):
        with TestService() as service:
            with MockServiceAutoregisterError():
                with MockServiceAutoregisterError2():
                    with LogCapture(level=log.ERROR) as l:
                        service.event.trigger()
                        time.sleep(1)  # wait for the callbacks

                        logged = []
                        for name, type_, _ in l.actual():
                            logged.append((name, type_))

                        expected_log = [("LogServer.Event", "ERROR")] * 2
                        self.assertEqual(logged, expected_log)


class CallbackTests(unittest.TestCase):

    def setUp(self):
        NameServer.start()
        log.LogServer.start()
        log.set_loglevel(log.DEBUG)

    def test_normalFunctionCall_Called(self):
        test_obj = MockService()
        test_obj.callback_function()
        self.assertTrue(test_obj.called())

    def test_normalFunctionCall_CorrectArgument(self):
        test_obj = MockService()
        test_obj.callback_function("Test")
        self.assertTrue(test_obj.arg(), "Test")

    def test_normalFunctionCallUsingKeyWordArg_CorrectArgument(self):
        test_obj = MockService()
        test_obj.callback_function(arg="Test")
        self.assertEqual(test_obj.arg(), "Test")

    def test_toString(self):
        with MockService() as test_obj:
            name = test_obj.callback_function.to_string()
            self.assertEqual(name, "MockService.callback_function")

    def test_callbackCall_Called(self):
        with TestService():
            with MockService() as test_obj:
                test_obj.perform_callback()
                self.assertTrue(test_obj.called())

    def test_callbackCall_CorrectArgument(self):
        with TestService():
            with MockService() as test_obj:
                test_obj.perform_callback("Test")
                self.assertEqual(test_obj.arg(), "Test")

    def test_callbackCallUsingKeyWordArg_CorrectArgument(self):
        with TestService():
            with MockService() as test_obj:
                test_obj.perform_callback_with_kwarg(arg="Test")
                self.assertEqual(test_obj.arg(), "Test")


class CallbackServiceTests(unittest.TestCase):

    def setUp(self):
        NameServer.start()
        log.LogServer.start()
        log.set_loglevel(log.DEBUG)

    def test_StartMultiplexedCallbackService_ErrorRaised(self):
        with self.assertRaises(ServerError):
            CallbackService.start(multiplex=True)
