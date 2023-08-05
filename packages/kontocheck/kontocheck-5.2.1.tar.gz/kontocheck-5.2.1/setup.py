#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup
from distutils.extension import Extension
from distutils.command.install import INSTALL_SCHEMES
import struct

_PY_BIT = struct.calcsize('P') * 8

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

data_files = [
    ('kontocheck/data', ['data/blz.lut2']),
    ]
        
if os.name == 'nt':
    data_files.append(
        ('kontocheck/lib', ['lib/kontocheck%s.dll' % _PY_BIT]))
    ext_modules = None
else:
    ext_modules = [
        Extension('kontocheck.lib.kontocheck',
            sources=['lib/konto_check/konto_check.c'],
        ),
    ]

dist = setup(
    name='kontocheck',
    version='5.2.1',
    author='Thimo Kraemer',
    author_email='thimo.kraemer@joonis.de',
    url='http://www.joonis.de/de/software/sepa-ebics-client/kontocheck',
    description='Python ctypes wrapper of the konto_check library.',
    long_description=read('README.rst'),
    keywords=('kontocheck', 'iban'),
    download_url='',
    license='LGPLv3',
    ext_modules=ext_modules,
    package_dir={'kontocheck': 'src'},
    packages=['kontocheck'],
    data_files=data_files,
    )
