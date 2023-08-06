#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
PYQTGRAPH EXAMPLE
-----------------

Additional requirements:

- PySide
- numpy
- pyqtgraph

Plots some random numbers using pyqtgraph.


.. created on 27.01.2014

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-In
import time

# External
from numpy.random import normal
import PyroMP
import PyroMP.log_server as log

from PySide.QtCore import QObject, Signal
import pyqtgraph


class PlotWindowManager(QObject):
    """Manages the plot window
    """

    # Signal is used instead of function call
    # normal calls are not possible because Qt has problems with threads
    add_value = Signal(object)

    def __init__(self):
        super(PlotWindowManager, self).__init__()
        # show an empty window
        # QtService without any window will be stopped
        labels = {"left": ("gaussian distribution (mean=6, variance=4)", ),
                 "bottom": ("x-axis", )}
        self._plot_window = pyqtgraph.plot(title="pyqtgraph example",
                                           labels=labels)

        self.add_value.connect(self._add_value)
        self._x_pos = 0
        self._old_value = None

    def _add_value(self, value):
        """Adds an additional point to the plot
        """
        if self._old_value is not None:
            self._plot_window.plot([self._x_pos - 1, self._x_pos],
                                   [self._old_value, value])
        self._x_pos += 1
        self._old_value = value


class PlotService(PyroMP.QtService):

    def qt_main(self):
        """Create the gui
        """
        self._window_manager = PlotWindowManager()

    def add_value(self, value):
        """Adds an additional point to the plot
        """
        # Signal is used instead of function call
        # normal calls are not possible because Qt has problems with threads
        self._window_manager.add_value.emit(value)


def main():
    # start NameServer and LogServer
    with PyroMP.NameServer(), log.LogServer():
        # start PlotService
        with PlotService(async=False) as service:

            # loop until window is closed
            while PlotService.is_running():
                # create Random value
                mean = 6
                std_dev = 2
                data_point = normal(mean, std_dev)

                # plot value
                service.add_value(data_point)

                # wait one second
                time.sleep(1)

if __name__ == "__main__":
    main()
