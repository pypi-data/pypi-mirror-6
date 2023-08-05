kontocheck
==========

Python extension module of the konto_check library.

This module is based on konto_check_, a small library to check German
bank accounts. It implements all check methods and IBAN generation
rules, published by the German Central Bank.

.. _konto_check: http://kontocheck.sourceforge.net

Requirements
------------

The source distribution requires the Cython_ package for compilation.

.. _Cython: http://cython.org

Example
-------

.. sourcecode:: python
    
    import kontocheck
    kontocheck.lut_load()
    bankname = kontocheck.get_name('37040044')
    iban = kontocheck.create_iban('37040044', '532013000')
    kontocheck.check_iban(iban)
    bic = kontocheck.get_bic(iban)
