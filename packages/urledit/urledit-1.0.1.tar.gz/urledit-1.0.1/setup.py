#!/usr/bin/env python
import os
import sys
import doctest
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

import urledit


DOC = urledit.__doc__.strip()

open('README.md', 'w').write(DOC)
if sys.argv[-1] == 'publish':
    if not doctest.testfile('README.md', verbose=True).failed:
        os.system('python setup.py sdist upload')
        sys.exit(1)

setup(
    name         = 'urledit',
    url          = 'https://github.com/imbolc/urledit',
    version      = urledit.__version__,
    description  = DOC.split('===\n')[1].strip().split('\n\n')[0],
    long_description = urledit.__doc__,

    py_modules   = ['urledit'],

    author       = 'Imbolc',
    author_email = 'imbolc@imbolc.name',
    license      = 'MIT',

    classifiers  = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
    ],
)
