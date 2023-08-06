#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
LOCAL SERVICE EXAMPLE
---------------------

Example implementation how to use a service as normal
python object instead of running in another process or thread


.. created on 19.02.2014

.. codeauthor:: Philipp Brimmers
                <P.Brimmers@yahoo.de>
'''

from __future__ import print_function, unicode_literals, division

# built-in
import os

# Intern
import PyroMP
import PyroMP.log_server as log


class FileService(PyroMP.Service):

    FILENAME = "test.txt"

    def init_resources(self):
        super(FileService, self).init_resources()
        # create empty file
        text = "LOGFILE:\n--------\n"
        with open(self.FILENAME, 'w') as f:
            f.write(text.encode('utf8'))

    def close_resources(self):
        super(FileService, self).close_resources()
        # print file using logging
        logger = self.get_logger()
        with open(self.FILENAME, 'r') as f:
            logger.info("\n" + f.read().decode('utf8'))
        # delete the file
        os.remove(self.FILENAME)

    def write_line(self, text):
        with open(self.FILENAME, 'a') as f:
            f.write((text + "\n").encode('utf8'))


def main():
    # disable the name server
    # to prevent from using an already running one
    PyroMP.NameServer.disable()
    # create service object
    service = FileService()
    # initialize the service and create log file
    service.init_resources()
    # write some lines
    service.write_line("first log entry")
    service.write_line("second log entry")
    service.write_line("third log entry")
    service.write_line("special characters: *°äöüàáì€$&%")
    # close the service object
    # print log file and delete it
    service.close_resources()

if __name__ == "__main__":
    log.set_loglevel("INFO")
    main()
