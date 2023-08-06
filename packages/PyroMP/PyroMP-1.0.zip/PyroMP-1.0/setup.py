#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 18.05.2012
author: Philipp Brimmers
"""

import os
from setuptools import setup, find_packages

DISTNAME = 'PyroMP'
DESCRIPTION = ('Easy muliprocessing combining Pyro4 '
               'and the built-in multiprocessing module')
LONG_DESCRIPTION = open("README.txt").read()
LICENSE = open("LICENSE.txt").read()
MAINTAINER = "Philipp Brimmers"
MAINTAINER_EMAIL = "P.Brimmers@yahoo.de"
URL = "https://bitbucket.org/PBrimmers/PyroMP"
DOWNLOAD_URL = ""
VERSION = "1.0"
PYTHON_VERSION = (2, 7)


def write_version_py(filename='PyroMP/version.py'):
    """Write version to module inside package"""
    template = """# THIS FILE IS GENERATED FROM THE METADATA SETUP.PY DO NOT EDIT!
version = "{}"
"""
    this_folder = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(this_folder, filename)
    with open(version_file, "w") as vfile:
        vfile.write(template.format(VERSION))

if __name__ == "__main__":
    write_version_py()
    setup(name=DISTNAME,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          url=URL,
          license=LICENSE,
          download_url=DOWNLOAD_URL,
          version=VERSION,
          install_requires=['Pyro4>=4.20',
                            'mock',
                            'six'],
          packages=find_packages(),
          test_suite='nose.collector',
          tests_require=['Nose', 'testfixtures']
          )
