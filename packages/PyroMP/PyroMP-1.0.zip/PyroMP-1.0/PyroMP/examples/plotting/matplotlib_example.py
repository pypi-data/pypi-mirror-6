#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
MATPLOTLIB EXAMPLE
------------------

Additional requirements:

- PySide
- numpy
- matplotlib

Plots some random numbers using matplotlib.


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

from PySide.QtCore import Signal
from PySide.QtGui import QDialog, QVBoxLayout

import matplotlib
# force matplotlib to use PySide
matplotlib.rcParams['backend.qt4'] = 'PySide'
if not matplotlib.get_backend() == 'Qt4Agg':
    matplotlib.use('Qt4Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar


class MatplotlibDialog(QDialog):

    add_value = Signal(object)

    def __init__(self):
        super(MatplotlibDialog, self).__init__()

        # create matplotlib gui elements
        # 8 inches wide and 6 inches high with a resolution of 80 dpi
        size = (8, 6)  # inch
        dpi = 80
        self._create_gui(size, dpi)

        # create the axes
        # use add_subplot instead of add_axis to enable subplot toolbox
        self._axes = self._fig.add_subplot(111)
        self._axes.set_xlabel("x-axis")
        self._axes.set_ylabel("gaussian distribution (mean=6, variance=0.04)")

        self.add_value.connect(self._add_value)
        self._x_value = 0

        self.setWindowTitle("matplotlib example")

    def _create_gui(self, size, dpi):
        # create figure
        self._fig = Figure(size, dpi=dpi)
        # create canvas widget
        self._canvas = FigureCanvas(self._fig)
        # create toolbar widget and connect it to canvas
        mpl_toolbar = NavigationToolbar(self._canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(mpl_toolbar)
        layout.addWidget(self._canvas)
        self.setLayout(layout)

    def _add_value(self, value):
        self._axes.scatter([self._x_value], [value])
        self._canvas.draw()
        self._x_value += 1


class PlotService(PyroMP.QtService):

    def qt_main(self):
        """Create the gui
        """
        self._dlg = MatplotlibDialog()
        # show the empty window
        # QtService without any window will be stopped
        self._dlg.show()

    def add_value(self, value):
        """Adds an additional point to the plot
        """
        # Signal is used instead of function call
        # normal calls are not possible because Qt has problems with threads
        self._dlg.add_value.emit(value)


def main():
    # start NameServer and LogServer
    with PyroMP.NameServer(), log.LogServer():
        # start PlotService
        with PlotService(async=False) as service:

            # loop until window is closed
            while PlotService.is_running():
                # create Random value
                mean = 6
                std_dev = 0.2
                data_point = normal(mean, std_dev)

                # plot value
                service.add_value(data_point)

                # wait one second
                time.sleep(1)

if __name__ == "__main__":
    main()
