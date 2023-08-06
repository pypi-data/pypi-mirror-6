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
import gc
import time

# Extern
import mock
from testfixtures import Replacer, LogCapture

# Intern
import PyroMP.log_server as log
from PyroMP.server import NameServer
from PyroMP.service import Service
from PyroMP.callback import (callback,
                              CallbackObject,
                              CallbackServer,
                              CallbackServerAlreadyRunningError,
                              CallbackServerNotRunningError,
                              Event)


class CallbackMock(CallbackObject):

    def __init__(self):
        super(CallbackMock, self).__init__()
        self.called = False
        self.arg = None

    @callback
    def callback_function(self, arg=None):
        self.called = True
        self.arg = arg


class ErrorCallbackMock(CallbackObject):

    def __init__(self):
        super(ErrorCallbackMock, self).__init__()
        self.called = False

    @callback
    def error_callback(self):
        self.called = True
        return 1 / 0


class TestService(Service):

    def __init__(self, multiplex=True, async=False):
        super(TestService, self).__init__(multiplex, async)
        self.event = Event()

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
        CallbackServer.start()

    def tearDown(self):
        CallbackServer.stop()

    def test_TriggerAfterUnregister_CallbackNotCalled(self):
        with TestService() as service:
            test_obj = CallbackMock()
            service.event.register(test_obj.callback_function)
            service.event.unregister(test_obj.callback_function)
            service.event.trigger()
            time.sleep(0.2)  # wait for the possible callback
            self.assertFalse(test_obj.called)

    def test_TriggerDirectly_CallbackCalled(self):
        with TestService() as service:
            test_obj = CallbackMock()
            service.event.register(test_obj.callback_function)
            service.event.trigger()
            time.sleep(0.2)  # wait for the callback
            self.assertTrue(test_obj.called)

    def test_TriggerUsingFunction_CallbackCalled(self):
        with TestService() as service:
            test_obj = CallbackMock()
            service.event.register(test_obj.callback_function)
            service.trigger_event()
            time.sleep(0.2)  # wait for the callback
            self.assertTrue(test_obj.called)

    def test_TriggerDirectlyWithArg_CallbackCalled(self):
        with TestService() as service:
            test_obj = CallbackMock()
            service.event.register(test_obj.callback_function)
            service.event.trigger("Test")
            time.sleep(0.2)  # wait for the callback
            self.assertEqual(test_obj.arg, "Test")

    def test_TriggerUsingFunctionWithArg_CallbackCalled(self):
        with TestService() as service:
            test_obj = CallbackMock()
            service.event.register(test_obj.callback_function)
            service.send_message("Test")
            time.sleep(0.2)  # wait for the callback
            self.assertEqual(test_obj.arg, "Test")

    def test_TriggerDirectlyWithKwarg_CallbackCalled(self):
        with TestService() as service:
            test_obj = CallbackMock()
            service.event.register(test_obj.callback_function)
            service.event.trigger(arg="Test")
            time.sleep(0.2)  # wait for the callback
            self.assertEqual(test_obj.arg, "Test")

    def test_TriggerUsingFunctionWithKwarg_CallbackCalled(self):
        with TestService() as service:
            test_obj = CallbackMock()
            service.event.register(test_obj.callback_function)
            service.send_message_with_kwarg("Test")
            time.sleep(0.2)  # wait for the callback
            self.assertEqual(test_obj.arg, "Test")

    def test_triggerWithErrors_allCallbacksCalled(self):
        with TestService() as service:
            test_obj1 = ErrorCallbackMock()
            test_obj2 = ErrorCallbackMock()
            test_obj3 = ErrorCallbackMock()
            service.event.register(test_obj1.error_callback)
            service.event.register(test_obj2.error_callback)
            service.event.register(test_obj3.error_callback)
            service.event.trigger()
            time.sleep(1)  # wait for the callbacks
            called_tuple = (test_obj1.called,
                            test_obj2.called,
                            test_obj3.called)
            self.assertEqual(called_tuple, (True, True, True))

    def test_triggerWithErrors_errorsLogged(self):
        with TestService() as service:
            with LogCapture(level=log.ERROR) as l:
                test_obj1 = ErrorCallbackMock()
                test_obj2 = ErrorCallbackMock()
                test_obj3 = ErrorCallbackMock()
                service.event.register(test_obj1.error_callback)
                service.event.register(test_obj2.error_callback)
                service.event.register(test_obj3.error_callback)
                service.event.trigger()
                time.sleep(1)  # wait for the callbacks

                logged = []
                for name, type_, _ in l.actual():
                    logged.append((name, type_))

                expected_log = [("LogServer.Event", "ERROR")] * 3
                self.assertEqual(logged, expected_log)


class CallbackTests(unittest.TestCase):

    def setUp(self):
        NameServer.start()
        log.LogServer.start()
        log.set_loglevel(log.DEBUG)
        CallbackServer.start()

    def tearDown(self):
        CallbackServer.stop()

    def test_toString(self):
        test_obj = CallbackMock()
        name = test_obj.callback_function.to_string()
        self.assertEqual(name, "CallbackMock.callback_function")

    def test_normalFunctionCall_Called(self):
        test_obj = CallbackMock()
        test_obj.callback_function()
        self.assertTrue(test_obj.called)

    def test_normalFunctionCall_CorrectArgument(self):
        test_obj = CallbackMock()
        test_obj.callback_function("Test")
        self.assertEqual(test_obj.arg, "Test")

    def test_normalFunctionCallUsingKeyWordArg_CorrectArgument(self):
        test_obj = CallbackMock()
        test_obj.callback_function(arg="Test")
        self.assertEqual(test_obj.arg, "Test")

    def test_callbackCall_Called(self):
        with TestService() as service:
            test_obj = CallbackMock()
            service.callback(test_obj.callback_function)
            self.assertTrue(test_obj.called)

    def test_callbackCall_CorrectArgument(self):
        with TestService() as service:
            test_obj = CallbackMock()
            service.callback(test_obj.callback_function, "Test")
            self.assertEqual(test_obj.arg, "Test")

    def test_callbackCallUsingKeyWordArg_CorrectArgument(self):
        with TestService() as service:
            test_obj = CallbackMock()
            service.callback_with_kwargs(test_obj.callback_function,
                                         arg="Test")
            self.assertEqual(test_obj.arg, "Test")


class CallbackRegisterUnregisterTest(unittest.TestCase):

    def setUp(self):
        NameServer.start()
        log.LogServer.start()
        log.set_loglevel(log.DEBUG)
        self.replacer = Replacer()
        self.daemon_mock = mock.MagicMock()
        self.replacer.replace("Pyro4.Daemon",
                              mock.Mock(return_value=self.daemon_mock))
        CallbackServer.start()

    def tearDown(self):
        try:
            CallbackServer.stop()
        except CallbackServerNotRunningError:
            pass

        self.replacer.restore()

    def test_createCallback_registered(self):
        proxy_stub = lambda x: x
        self.replacer.replace("weakref.proxy", proxy_stub)
        callback = CallbackMock()
        func = callback.callback_function
        id_ = callback.callback_function.id()
        self.daemon_mock.register.assert_called_once_with(func, id_)

    def test_deleteCallback_unregistered(self):
        callback = CallbackMock()
        id_ = callback.callback_function.id()
        # both have to be deleted cause of circular referencing
        del(callback.callback_function)
        del(callback)
        gc.collect()
        self.daemon_mock.unregister.assert_called_once_with(id_)


class CallbackServerTest(unittest.TestCase):

    def setUp(self):
        NameServer.start()
        log.LogServer.start()
        log.set_loglevel(log.DEBUG)
        CallbackServer.start()

    def tearDown(self):
        try:
            CallbackServer.stop()
        except CallbackServerNotRunningError:
            pass

    def test_startAgain_CallbackServerAlreadyRunningError(self):
        with self.assertRaises(CallbackServerAlreadyRunningError):
            CallbackServer.start()

    def test_stopTwice_CallbackServerNotRunningError(self):
        CallbackServer.stop()
        with self.assertRaises(CallbackServerNotRunningError):
            CallbackServer.stop()

    def test_stopThenRegister_CallbackServerNotRunningError(self):
        CallbackServer.stop()
        with self.assertRaises(CallbackServerNotRunningError):
            CallbackServer.register(None)
