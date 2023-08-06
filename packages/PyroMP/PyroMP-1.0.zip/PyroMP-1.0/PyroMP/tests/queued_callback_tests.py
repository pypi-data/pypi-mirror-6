#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 09.10.2013

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-in
import time
import unittest

# Intern
import PyroMP.log_server as log
from PyroMP.service import Service
from PyroMP.server import NameServer
from PyroMP.callback import (callback,
                              CallbackObject,
                              CallbackServer,
                              Event)
from PyroMP.queued_service import (QueuedService,
                                   ForbiddenAttributeAccessError)


class FakeEvent(object):

    def register(self, obj):
        pass


class CallbackMock(CallbackObject):

    def __init__(self):
        super(CallbackMock, self).__init__()
        self.called = False
        self.arg = None

    @callback
    def callback_function(self, arg=None):
        self.called = True
        self.arg = arg


class TestService(Service):

    def __init__(self, multiplex=True, async=False):
        super(TestService, self).__init__(multiplex, async)
        self.event = Event()
        self.fake_event = FakeEvent()

    def callback(self, callback, arg=None):
        callback.call(arg)

    def send_message(self, arg):
        self.event.trigger(arg)

    def trigger_event(self):
        self.event.trigger()


class QueuedTestService(QueuedService):

    CLASS = TestService

    def __init__(self, **kwargs):
        super(QueuedTestService, self).__init__(async=False, **kwargs)


class QueuedEventTests(unittest.TestCase):

    def setUp(self):
        NameServer.start()
        log.LogServer.start()
        log.set_loglevel(log.DEBUG)
        CallbackServer.start()

    def tearDown(self):
        CallbackServer.stop()

    def test_TriggerDirectly_ForbiddenAttributeAccessError(self):
        with QueuedTestService() as service:
            test_obj = CallbackMock()
            service.event.register(test_obj.callback_function)
            with self.assertRaises(ForbiddenAttributeAccessError):
                service.event.trigger()

    def test_RegisterAtFakeEvent_ForbiddenAttributeAccessError(self):
        with QueuedTestService() as service:
            test_obj = CallbackMock()
            with self.assertRaises(ForbiddenAttributeAccessError):
                service.fake_event.register(test_obj.callback_function)

    def test_TriggerUsingFunction_CallbackCalled(self):
        with QueuedTestService() as service:
            test_obj = CallbackMock()
            service.event.register(test_obj.callback_function)
            service.trigger_event()
            time.sleep(0.1)  # wait for callback to be performed
            self.assertTrue(test_obj.called)

    def test_TriggerAfterUnregister_CallbackNotCalled(self):
        with QueuedTestService() as service:
            test_obj = CallbackMock()
            service.event.register(test_obj.callback_function)
            service.event.unregister(test_obj.callback_function)
            service.trigger_event()
            time.sleep(0.1)  # wait for callback to be performed
            self.assertFalse(test_obj.called)

    def test_TriggerUsingFunctionWithArg_CallbackCalled(self):
        with QueuedTestService() as service:
            test_obj = CallbackMock()
            service.event.register(test_obj.callback_function)
            service.send_message("Test")
            time.sleep(0.1)  # wait for callback to be performed
            self.assertTrue(test_obj.arg, "Test")


class QueuedCallbackTest(unittest.TestCase):

    def setUp(self):
        NameServer.start()
        log.LogServer.start()
        log.set_loglevel(log.DEBUG)
        CallbackServer.start()

    def tearDown(self):
        logger = log.create_logger("QueuedCallbackTest")
        logger.debug("Stop callback server")
        CallbackServer.stop()
        logger.debug("Tear down finished")

    def test_Called(self):
        logger = log.create_logger("Test_QueuedCB_Called")
        logger.debug("Start service")
        with QueuedTestService() as service:
            logger.debug("Create mock object")
            test_obj = CallbackMock()
            logger.debug("Call the function that does the callback")
            service.callback(test_obj.callback_function)
            logger.debug("Assert")
            self.assertTrue(test_obj.called)
            logger.debug("Stop service")
        logger.debug("Test finished")

    def test_CorrectArgument(self):
        with QueuedTestService() as service:
            test_obj = CallbackMock()
            service.callback(test_obj.callback_function, "Test")
            self.assertTrue(test_obj.arg, "Test")
