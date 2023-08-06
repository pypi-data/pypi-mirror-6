#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
LOG WINDOW EXAMPLE
------------------

Additional requirements:

- PySide or PyQt4

Starts a LogServer and display all logs in a QTextEdit.


.. created on 30.12.2013
.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-In

# External
from PyroMP.Qt import QtCore, QtGui

# Internal
import PyroMP
import PyroMP.log_server as log


class LogStream(object):
    """File-like object that appends the text to the LogDialog.

    Used for the StreamHandler.
    """

    def write(self, text):
        dlg_conn = LogDialogService.get_connection(async=False)
        dlg_conn.connect()
        dlg_conn.append_log(text)


class LogDialog(QtGui.QDialog):

    append_log_signal = QtCore.Signal(object)

    def __init__(self):
        super(LogDialog, self).__init__()

        layout = QtGui.QVBoxLayout()

        self._text_edit = QtGui.QTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setFont("Courier New")
        layout.addWidget(self._text_edit)
        self.setLayout(layout)

        self.append_log_signal.connect(self.append_log)
        self.setWindowTitle("Log Window")

    def append_log(self, text):
        text = self._text_edit.toPlainText() + text
        self._text_edit.setPlainText(text)


class LogDialogService(PyroMP.QtService):

    LOGGING = False

    def qt_main(self):
        """Create the gui elements
        """
        logger = self.get_logger()
        logger.debug("Create dialog")
        self._dlg = LogDialog()
        logger.debug("Show dialog")
        # QtService without any window will be stopped
        self._dlg.show()

        # Configure logging for log server loggers
        root_logger = log.get_server_root_logger()
        log_stream = LogStream()
        root_logger.add_streamhandler(log_stream)

    def append_log(self, text):
        # Signal is used instead of function call
        # normal calls are not possible because Qt has problems with threads
        self._dlg.append_log_signal.emit(text)


def main():
    with LogDialogService():
        LogDialogService.wait_for()


if __name__ == '__main__':
    with PyroMP.NameServer(), log.LogServer():
        main()
