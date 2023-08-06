#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This code runs this example.

Adapted from Pyro4 warehouse example
http://pythonhosted.org/Pyro4/tutorials.html
'''

from __future__ import print_function, unicode_literals, division

# Intern
import PyroMP
import PyroMP.log_server as log
from warehouse import Warehouse
from person import Person


def main():
    with PyroMP.NameServer(), log.LogServer():
        log.set_loglevel("INFO")
        with Warehouse() as warehouse:
            janet = Person("Janet")
            henry = Person("Henry")
            janet.visit(warehouse)
            henry.visit(warehouse)

if __name__ == "__main__":
        main()
