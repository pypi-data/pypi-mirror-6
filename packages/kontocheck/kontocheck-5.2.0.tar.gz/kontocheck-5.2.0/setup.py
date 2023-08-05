#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup
from distutils.extension import Extension
from distutils.command.install import INSTALL_SCHEMES
from Cython.Distutils import build_ext

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

extensions = [
    Extension('kontocheck.konto_check',
        ['src/konto_check.pyx', 'src/konto_check/konto_check.c'],
    ),
]

setup(
    name='kontocheck',
    version='5.2.0',
    author='Thimo Kraemer',
    author_email='thimo.kraemer@joonis.de',
    url='http://www.joonis.de/de/software/sepa-ebics-client/kontocheck',
    description='Python extension module of the konto_check library',
    long_description=read('README.rst'),
    keywords=('kontocheck', 'iban'),
    download_url='',
    license='LGPLv3',
    cmdclass={'build_ext': build_ext},
    ext_modules=extensions,
    package_dir={'kontocheck': 'src'},
    packages=['kontocheck'],
    #package_data={'kontocheck': ['konto_check/blz.lut2']},
    data_files=[
        ('kontocheck/data', ['src/konto_check/blz.lut2']),
        ],
    requires=[],
    )
