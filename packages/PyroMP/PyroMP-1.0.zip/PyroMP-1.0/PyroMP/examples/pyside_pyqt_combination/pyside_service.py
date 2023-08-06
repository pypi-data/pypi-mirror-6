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
from PySide.QtGui import (QVBoxLayout,
                          QDialog,
                          QTextEdit)

# Internal
import PyroMP
import PyroMP.log_server as log


class PyQtDialogService(PyroMP.QtService):
    pass


class OutputDialog(QDialog):

    def __init__(self):
        super(OutputDialog, self).__init__()

        layout = QVBoxLayout()

        self._proxy = PyQtDialogService.get_connection()
        self._proxy.connect()

        self._text_edit = QTextEdit()
        self._text_edit.textChanged.connect(self.forward_text)
        layout.addWidget(self._text_edit)
        self.setLayout(layout)

        self.setWindowTitle("PySide Dialog")

    def forward_text(self):
        text = self._text_edit.toPlainText()
        self._proxy.print_(text)


class PySideDialogService(PyroMP.QtService):

    def qt_main(self):
        logger = self.get_logger()
        logger.debug("Create dialog")
        self._dlg = OutputDialog()
        logger.debug("Show dialog")
        # QtService without any window will be stopped
        self._dlg.show()


def main():
    with PySideDialogService():
        # blocks until window is closed
        PySideDialogService.wait_for()


if __name__ == '__main__':
    with PyroMP.NameServer(), log.LogServer():
        main()
