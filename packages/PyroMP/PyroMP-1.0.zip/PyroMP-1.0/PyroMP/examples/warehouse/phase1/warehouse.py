#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Adapted from Pyro4 warehouse example
http://pythonhosted.org/Pyro4/tutorials.html
'''

from __future__ import print_function, unicode_literals, division

# Built-in
import logging


class Warehouse(object):

    def __init__(self):
        self.contents = ["chair", "bike", "flashlight", "laptop", "couch"]
        self.logger = logging.getLogger("Warehouse")

    def list_contents(self):
        return self.contents

    def take(self, name, item):
        self.contents.remove(item)
        self.logger.info("{0} took the {1}.".format(name, item))

    def store(self, name, item):
        self.contents.append(item)
        self.logger.info("{0} stored the {1}.".format(name, item))
