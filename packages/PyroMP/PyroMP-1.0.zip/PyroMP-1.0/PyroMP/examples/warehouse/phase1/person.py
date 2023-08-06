#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Adapted from Pyro4 warehouse example
http://pythonhosted.org/Pyro4/tutorials.html
'''

from __future__ import print_function, unicode_literals, division

# Extern
from six.moves import input


class Person(object):

    def __init__(self, name):
        self.name = name

    def visit(self, warehouse):
        print("This is {0}.".format(self.name))
        self.deposit(warehouse)
        self.retrieve(warehouse)
        print("Thank you, come again!")

    def deposit(self, warehouse):
        print("The warehouse contains: {}".format(
                                                warehouse.list_contents()))
        item = input("Type a thing you want to store (or empty): ").strip()
        if item:
            warehouse.store(self.name, item)

    def retrieve(self, warehouse):
        print("The warehouse contains: {}".format(
                                                warehouse.list_contents()))
        item = input("Type something you want to take (or empty): ").strip()
        if item:
            warehouse.take(self.name, item)

