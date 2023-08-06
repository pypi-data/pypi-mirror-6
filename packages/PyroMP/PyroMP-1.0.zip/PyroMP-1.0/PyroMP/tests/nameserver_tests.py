#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 16.12.2013

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division, absolute_import

# Built-In
import unittest

# Intern
import PyroMP
import PyroMP.server as server
from PyroMP import NameServer


class AnotherNameServer(server.ServerProcess):

    def _serve(self):
        try:
            NameServer.start()
            self._queue.put(self.READY)
            self._queue.get()
            NameServer.stop()
        except Exception as exc:
            self._queue.put(exc)


class TestNameServer(unittest.TestCase):

    def setUp(self):
        NameServer.stop()
        NameServer._running = None

    def tearDown(self):
        NameServer.stop()

    def test_startAndLocate_noError(self):
        NameServer.start()
        NameServer.locate()

    def test_notStartedAndLocate_NameServerError(self):
        with self.assertRaises(PyroMP.errors.NameServerError):
            NameServer.locate()

    def test_startRemotlyAndLocate_noError(self):
        server = AnotherNameServer(daemon=False,
                                   logging=False,
                                   thread=False)
        server.start()
        try:
            NameServer.locate()
        finally:
            server.stop()


class TestNameServerDisabled(unittest.TestCase):

    def setUp(self):
        NameServer.disable()
        NameServer._running = None

    def tearDown(self):
        NameServer.stop()
        NameServer.enable()

    def test_startAndLocate_NameServerError(self):
        NameServer.start()
        with self.assertRaises(PyroMP.errors.NameServerError):
            NameServer.locate()

    def test_notStartedAndLocate_NameServerError(self):
        with self.assertRaises(PyroMP.errors.NameServerError):
            NameServer.locate()

    def test_startRemotlyAndLocate_NameServerError(self):
        server = AnotherNameServer(daemon=False,
                                   logging=False,
                                   thread=False)
        server.start()
        try:
            with self.assertRaises(PyroMP.errors.NameServerError):
                NameServer.locate()
        finally:
            server.stop()


class TestNameServerEnabled(unittest.TestCase):

    def setUp(self):
        NameServer.disable()
        NameServer.enable()
        NameServer._running = None

    def tearDown(self):
        NameServer.stop()

    def test_startAndLocate_noError(self):
        NameServer.start()
        NameServer.locate()

    def test_notStartedAndLocate_NameServerError(self):
        with self.assertRaises(PyroMP.errors.NameServerError):
            NameServer.locate()

    def test_startRemotlyAndLocate_noError(self):
        server = AnotherNameServer(daemon=False,
                                   logging=False,
                                   thread=False)
        server.start()
        try:
            NameServer.locate()
        finally:
            server.stop()
