#!/usr/bin/env python

from inspect import stack, getmodule

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, Canari Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

__all__ = [
    'calling_module',
    'calling_package'
]


def calling_module(frame=2):
    frame = stack()[frame]
    return getmodule(frame[0])


def calling_package(frame=2):
    frame = stack()[frame]
    return getmodule(frame[0]).__name__.split('.')[0]