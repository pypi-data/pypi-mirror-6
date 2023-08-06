#!/usr/bin/env python

"""Setup script for packaging openpyxl.

Requires setuptools.

To build the setuptools egg use
    python setup.py bdist_egg
and either upload it to the PyPI with:
    python setup.py upload
or upload to your own server and register the release with PyPI:
    python setup.py register

A source distribution (.zip) can be built with
    python setup.py sdist --format=zip

That uses the manifest.in file for data files rather than searching for
them here.

"""

import sys
import os.path as osp
if sys.version_info < (2, 6):
    raise Exception("Python >= 2.6 is required.")

from setuptools import setup, Extension, find_packages

here = osp.abspath(osp.dirname(__file__))
try:
    with open(osp.join(here, 'README')) as f:
        README = f.read()
    with open(osp.join(here, 'CHANGES')) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ''

requires = ['python (>=2.6.0)']
install_requires = ['openpyxl >= 1.8.3']
if sys.version_info < (2, 7):
    install_requires.append('argparse >= 1.2.1')

scripts = [osp.join('xlsxdiff', 'bin', 'xlsxdiff'),
           osp.join('xlsxdiff', 'bin', 'xlsxdiff.bat'), ]

setup(name='xlsxdiff',
    packages=find_packages(),
    # metadata
    version='0.1',
    description="compares xlsx/xlsm files",
    long_description=README + '\n\n' + CHANGES,
    author='Eric Gazoni',
    author_email="eric.gazoni@adimian.com",
    url='https://bitbucket.org/adimian/xlsx-diff',
    license='MIT/Expat',
    requires=requires,
    install_requires=install_requires,
    scripts=scripts,
    classifiers=['Development Status :: 3 - Alpha',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          ],
    )
