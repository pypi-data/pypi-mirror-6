#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
PyroMP provides a seamless transition from object oriented
to service oriented programming.
It is based on :mod:`Pyro4` and :mod:`multiprocessing`.
The former is used for object oriented RPCs and the latter
for process generation.

PyroMP is distributed under the `MIT open-source license`_.

Requirements:
-------------

- Python 2.7 or higher
- :mod:`Pyro4` 4.20 or higher

.. note:: PyroMP is developed and tested using Pyro4 4.22 and Python 2.7.
    But also tested with Pyro4 4.23 and Python 3.3.

Testing:

- testfixtures

.. note:: The package is very well tested.
    If you are not sure to meet the requirements, run the tests and examples.
    If the tests pass and the examples work, it will be okay.

.. _MIT open-source license: http://www.opensource.org/licenses/mit-license.php

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from .service import (QtService,
                     Service,
                     ServiceConnection)
from .server import NameServer

from .callback import (callback,
                      CallbackFunction,
                      CallbackObject,
                      CallbackServer,
                      CallbackService,
                      Event)

from .queued_service import priority, QueuedService

from .version import version as __version__