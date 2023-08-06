#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 26.09.2013

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-in
import os
import unittest
import logging

# Extern
from testfixtures import LogCapture
from six.moves import cStringIO as StringIO

# Intern
import PyroMP.log_server as log
from PyroMP.server import NameServer, NameServerError

log.MAX_LOGGER_NAME_LEN = 20
log.NUM_START_LETTERS = 7

LOG_FILE1 = os.path.abspath("test1.log")
LOG_FILE2 = os.path.abspath("test2.log")


class BaseLoggingTests(object):

    def test_clear_read_file(self):
        self.clear_file(LOG_FILE1)
        self.assertEqual(self.read_file(LOG_FILE1), [])

    def clear_file(self, filename):
        with open(filename, 'w'):
            pass

    def read_file(self, filename):
        with open(filename) as f:
            log_str = f.read()

        log = log_str.split("\n")
        return log[:-1]

    def test_StandardLog(self):
        with LogCapture() as l:
            logger = log.create_logger("TestLogger")
            logger.error("Test message")
            l.check(("LogServer.TestLogger", "ERROR", "Test message"))

    def test_setLoglevel(self):
        log.set_loglevel(log.CRITICAL)
        with LogCapture() as l:
            logger = log.create_logger("TestLogger")
            logger.setLevel(log.NOTSET)  # reset level
            logger.error("Test message")
            logger.critical("Test message")
            l.check(("LogServer.TestLogger", "CRITICAL", "Test message"))

    def test_loggerRemoved_LoggerRemovedError(self):
        logger = log.create_logger("TestLogger")
        logger.remove()
        with self.assertRaises(KeyError):
            logger.error("Test message")

    def test_setFileHandler_loggedOneLogToFile(self):
        self.clear_file(LOG_FILE1)

        logger = log.create_logger("TestLogger")
        logger.add_filehandler(LOG_FILE1)
        logger.error("Test message")

        test_log = self.read_file(LOG_FILE1)

        self.assertEqual(len(test_log), 1)

    def test_setFileHandler_loggedCorrectLogToFile(self):
        self.clear_file(LOG_FILE1)

        logger = log.create_logger("TestLogger")
        logger.add_filehandler(LOG_FILE1)
        logger.error("Test message")

        ref_log = ("YYYY-MM-DD HH:MM:SS,uuu - LogServer.TestLogger          "
                   " - ERROR    - Test message")
        test_log = self.read_file(LOG_FILE1)[0]
        if len(test_log) > 23:  # only replace time string
                                # when the log entry is long enough
            test_log = "YYYY-MM-DD HH:MM:SS,uuu" + test_log[23:]

        self.assertEqual(test_log, ref_log)

    def test_setFileHandlerWithFormatter_loggedCorrectLogToFile(self):
        self.clear_file(LOG_FILE1)

        logger = log.create_logger("TestLogger")
        logger.add_filehandler(LOG_FILE1, log.Formatter())
        logger.error("Test message")

        ref_log = ("Test message")
        test_log = self.read_file(LOG_FILE1)[0]

        self.assertEqual(test_log, ref_log)


class LoggingWithoutServerTests(BaseLoggingTests, unittest.TestCase):

    def setUp(self):
        # stop already running LogServer
        try:
            log.LogServer.stop()
        except NameServerError:
            # no log server is running
            pass
        NameServer.stop()
        log._local_server = None

    def test_isRunning_False(self):
        self.assertFalse(log.LogServer.is_running())

    def test_logToRootLoggerHandler(self):
        root_logger = logging.getLogger("")
        root_logger.setLevel(log.DEBUG)
        stream = StringIO()
        stream_handler = logging.StreamHandler(stream)
        root_logger.addHandler(stream_handler)
        logger = log.create_logger("TestLogger")
        logger.setLevel(log.DEBUG)
        logger.debug("Test")
        self.assertEqual(stream.getvalue(), "Test\n")

    def test_logToRootLoggerHandler_AfterStartingLogServer(self):
        root_logger = logging.getLogger("")
        root_logger.setLevel(log.DEBUG)
        stream = StringIO()
        stream_handler = logging.StreamHandler(stream)
        root_logger.addHandler(stream_handler)
        with NameServer(), log.LogServer():
            logger = log.create_logger("TestLogger")
            logger.setLevel(log.DEBUG)
            logger.debug("Test")
        self.assertEqual(stream.getvalue(), "Test\n")


class LoggingWithServerTest(BaseLoggingTests, unittest.TestCase):

    def setUp(self):
        # stop already running LogServer
        try:
            log.LogServer.stop()
        except NameServerError:
            # no log server is running
            pass
        NameServer.start()
        log.LogServer.start()
        log.set_loglevel(log.ERROR)

    def tearDown(self):
        log.LogServer.stop()

    def test_isRunning_True(self):
        self.assertTrue(log.LogServer.is_running())

    def test_isRunning_stopServer_False(self):
        log.LogServer.stop()
        self.assertFalse(log.LogServer.is_running())
