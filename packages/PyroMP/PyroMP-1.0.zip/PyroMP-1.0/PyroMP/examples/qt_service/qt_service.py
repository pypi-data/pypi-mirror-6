#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
QT SERVICE EXAMPLE
------------------

Additional requirements:

- PySide or PyQt4

Demonstrates the need of using the signal/slot
mechanism instead of normal function calls.

The control dialog can start a output window either using a threaded or
a multiplexed server.
The service provides to function to print text.
One uses normal function calls, the other forwards the
text to the function using the signal/slot mechanism.

Try it and see what happens.

.. Created on 30.12.2013

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# Built-In

# External

# Internal
import PyroMP
import PyroMP.log_server as log
from PyroMP.Qt import QtCore, QtGui


class OutputDialog(QtGui.QDialog):

    print_signal = QtCore.Signal(object)

    def __init__(self):
        super(OutputDialog, self).__init__()
        self._text_edit = QtGui.QTextEdit()
        self._text_edit.setReadOnly(True)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self._text_edit)
        self.setLayout(layout)

        self.print_signal.connect(self.print_)
        self.setWindowTitle("Output")

    def print_(self, text):
        """Add a new line, that contains ``text`` to the QTextEdit"""
        text = self._text_edit.toPlainText() + text + "\n"
        self._text_edit.setPlainText(text)


class OutputDialogService(PyroMP.QtService):

    def qt_main(self):
        logger = self.get_logger()
        logger.debug("Create dialog")
        self._dlg = OutputDialog()
        logger.debug("Show dialog")
        # QtService without any window will be stopped
        self._dlg.show()

    def print_with_signal(self, text):
        """emits a signal, that calls the print_ function"""
        self._dlg.print_signal.emit(text)

    def print_with_function_call(self, text):
        """calls print_ function directly"""
        self._dlg.print_(text)


class ControlDialog(QtGui.QDialog):

    def __init__(self):
        super(ControlDialog, self).__init__()

        layout = QtGui.QVBoxLayout()

        control_layout = QtGui.QHBoxLayout()

        self._start_button = QtGui.QPushButton("Start")
        self._start_button.clicked.connect(self.start_output_dialog_service)
        control_layout.addWidget(self._start_button)

        self._server_mode_box = QtGui.QComboBox()
        self._server_mode_box.addItems(["threaded",
                                        "multiplexed"])
        control_layout.addWidget(self._server_mode_box)

        self._stop_button = QtGui.QPushButton("Stop")
        self._stop_button.setDisabled(True)
        self._stop_button.clicked.connect(self.stop_output_dialog_service)
        control_layout.addWidget(self._stop_button)

        layout.addLayout(control_layout)

        self._text_edit = QtGui.QLineEdit()
        layout.addWidget(self._text_edit)
        self.setLayout(layout)

        send_layout = QtGui.QHBoxLayout()

        self._send_button = QtGui.QPushButton("Send (function call)")
        self._send_button.setDisabled(True)
        self._send_button.clicked.connect(self.print_with_function_call)
        send_layout.addWidget(self._send_button)

        self._send_signal_button = QtGui.QPushButton("Send (signal/slot)")
        self._send_signal_button.setDisabled(True)
        self._send_signal_button.clicked.connect(self.print_with_signal)
        send_layout.addWidget(self._send_signal_button)

        layout.addLayout(send_layout)

        self.setWindowTitle("Control Dialog")

    def print_with_signal(self):
        text = self._text_edit.text()
        dlg_conn = OutputDialogService.get_connection(async=False)
        dlg_conn.connect()
        dlg_conn.print_with_signal(text)
        self._text_edit.clear()

    def print_with_function_call(self):
        text = self._text_edit.text()
        dlg_conn = OutputDialogService.get_connection(async=False)
        dlg_conn.connect()
        dlg_conn.print_with_function_call(text)
        self._text_edit.clear()

    def start_output_dialog_service(self):
        # Disable buttons
        self._start_button.setDisabled(True)
        self._server_mode_box.setDisabled(True)

        # Stop service
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        multiplex = self._server_mode_box.currentIndex() == 1
        try:
            OutputDialogService.start(multiplex)
        finally:
            QtGui.QApplication.restoreOverrideCursor()

        # Enable buttons
        self._stop_button.setEnabled(True)
        self._send_button.setEnabled(True)
        self._send_signal_button.setEnabled(True)

    def stop_output_dialog_service(self):
        # Disable buttons
        self._stop_button.setDisabled(True)
        self._send_button.setDisabled(True)
        self._send_signal_button.setDisabled(True)

        # Stop service
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            OutputDialogService.stop()
        finally:
            QtGui.QApplication.restoreOverrideCursor()

        # Enable buttons
        self._start_button.setEnabled(True)
        self._server_mode_box.setEnabled(True)


def main():
    app = QtGui.QApplication([])
    dialog = ControlDialog()
    dialog.show()
    app.exec_()


if __name__ == '__main__':
    with PyroMP.NameServer(), log.LogServer():
        main()
