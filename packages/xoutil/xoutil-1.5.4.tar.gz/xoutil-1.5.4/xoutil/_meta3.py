#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil._meta3
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-04-29

'''Implements the meta() function using the Py3k syntax.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.six import PY3
assert PY3, 'This module should be loaded in Py3k only'


def metaclass(meta):
    class base:
        pass

    class inner_meta(meta.__base__):
        def __new__(cls, name, bases, attrs):
            if name != '__inner__':
                bases = tuple(b for b in bases if not issubclass(b, base))
                if not bases:
                    bases = (object,)
                return meta(name, bases, attrs)
            else:
                return type.__new__(cls, name, bases, attrs)

        def __init__(self, name, bases, attrs):
            pass

    # Hide this stuff from Python 2.7 compiler so several static analysis tools
    # (like pylint and other) don't complain about a SyntaxError.
    eval(compile('class __inner__(base, metaclass=inner_meta):pass',
                 __file__, 'exec'))

    return locals()['__inner__']
