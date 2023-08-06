#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Adapted from Pyro4 warehouse example
http://pythonhosted.org/Pyro4/tutorials.html
'''

from __future__ import print_function, unicode_literals, division

# Intern
import PyroMP


class Warehouse(PyroMP.Service):

    def __init__(self, async=False, multiplex=False):
        super(Warehouse, self).__init__(async, multiplex)
        self.contents = ["chair", "bike", "flashlight", "laptop", "couch"]
        self.logger = self.get_logger()

    def list_contents(self):
        return self.contents

    def take(self, name, item):
        self.contents.remove(item)
        self.logger.info("{0} took the {1}.".format(name, item))

    def store(self, name, item):
        self.contents.append(item)
        self.logger.info("{0} stored the {1}.".format(name, item))

