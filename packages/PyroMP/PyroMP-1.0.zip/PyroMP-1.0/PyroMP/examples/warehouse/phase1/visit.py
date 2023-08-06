#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This code runs this example.

Adapted from Pyro4 warehouse example
http://pythonhosted.org/Pyro4/tutorials.html
'''

from __future__ import print_function, unicode_literals, division

# Built-in
import logging

# Intern
from warehouse import Warehouse
from person import Person


def main():
    root_logger = logging.getLogger()
    root_logger.addHandler(logging.StreamHandler())
    root_logger.setLevel("INFO")
    warehouse = Warehouse()
    janet = Person("Janet")
    henry = Person("Henry")
    janet.visit(warehouse)
    henry.visit(warehouse)

if __name__ == "__main__":
    main()
