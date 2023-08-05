kontocheck
==========

Python ctypes wrapper of the konto_check library.

This module is based on konto_check_, a small library to check German
bank accounts. It implements all check methods and IBAN generation
rules, published by the German Central Bank.

.. _konto_check: http://kontocheck.sourceforge.net


Example
-------

.. sourcecode:: python
    
    import kontocheck
    kontocheck.lut_load()
    bankname = kontocheck.get_name('37040044')
    iban = kontocheck.create_iban('37040044', '532013000')
    kontocheck.check_iban(iban)
    bic = kontocheck.get_bic(iban)


Changelog
---------

v5.2.1
    Replaced Cython with ctypes, since it is easier to maintain for
    different plattforms.
