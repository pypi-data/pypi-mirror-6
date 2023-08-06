#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This code runs a second process for this example.

Adapted from Pyro4 warehouse example
http://pythonhosted.org/Pyro4/tutorials.html
'''

from __future__ import print_function, unicode_literals, division

# Intern
from person import Person
from warehouse import Warehouse


def main():
    # no need to start NameServer or LogServer
    # because we assume they are still running
    with Warehouse(async=False) as warehouse:
        josephine = Person("Josephine")
        peter = Person("Peter")
        josephine.visit(warehouse)
        peter.visit(warehouse)

if __name__ == "__main__":
    main()
