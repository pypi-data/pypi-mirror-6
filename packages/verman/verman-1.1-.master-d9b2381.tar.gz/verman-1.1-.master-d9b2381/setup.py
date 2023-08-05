#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Copyright (c) 2013, The BiPy Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

__credits__ = ["Daniel McDonald"]
__license__ = 'BSD'

from verman import verman_version

__version__ = str(verman_version)

from setuptools import setup
import sys

classes = """
    Development Status :: 5 - Production/Stable
    License :: OSI Approved :: BSD License
    Topic :: Software Development
    Programming Language :: Python
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: Implementation :: CPython
    Operating System :: OS Independent
"""
classifiers = [s.strip() for s in classes.split('\n') if s]

# Verify Python version
ver = '.'.join(map(str, [sys.version_info.major, sys.version_info.minor]))
if ver not in ['2.7', '3.3']:
    sys.stderr.write("Only Python 2.7 and 3.3 are supported.")
    sys.exit(1)

long_description = """verman is a simple package intended to standardize how version information is represented."""

setup(name='verman',
      version=__version__,
      license=__license__,
      description='verman: version management',
      long_description=long_description,
      author="Daniel McDonald",
      author_email="mcdonadt@colorado.edu",
      maintainer="Daniel McDonald",
      maintainer_email="mcdonadt@colorado.edu",
      url='https://github.com/wasade/verman',
      packages=['verman'],
      install_requires=[],
      classifiers=classifiers
      )
