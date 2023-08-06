#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
PYSIDE PYQT EXAMPLE
-------------------

Additional requirements:

- PySide AND PyQt4

Send text from PySide to PyQt widget.

Start pyqt_service.py first and then pyside_service.py.
You can write text into the PySide widget and
it will be forwarded to the PyQt4 one.


.. created on 30.12.2013

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-In

# External
from PyQt4.QtGui import (QVBoxLayout,
                          QDialog,
                          QTextEdit)
from PyroMP.Qt import QtCore

# Internal
import PyroMP
import PyroMP.log_server as log


class PySideDialogService(PyroMP.QtService):
    pass


class OutputDialog(QDialog):

    append_log_signal = QtCore.Signal(object)

    def __init__(self):
        super(OutputDialog, self).__init__()

        layout = QVBoxLayout()

        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        layout.addWidget(self._text_edit)
        self.setLayout(layout)

        self.append_log_signal.connect(self.print_)
        self.setWindowTitle("PyQt Dialog")

    def print_(self, text):
        self._text_edit.setPlainText(text)


class PyQtDialogService(PyroMP.QtService):

    def qt_main(self):
        logger = self.get_logger()
        logger.debug("Create dialog")
        self._dlg = OutputDialog()
        logger.debug("Show dialog")
        # QtService without any window will be stopped
        self._dlg.show()

    def print_(self, text):
        # Signal is used instead of function call
        # normal calls are not possible because Qt has problems with threads
        self._dlg.append_log_signal.emit(text)


def main():
    with PyQtDialogService():
        # blocks until window is closed
        PyQtDialogService.wait_for()


if __name__ == '__main__':
    with PyroMP.NameServer(), log.LogServer():
        main()
