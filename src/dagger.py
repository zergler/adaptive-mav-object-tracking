#!/usr/bin/env python2.7

""" Implements the DAgger algorithm
"""

from PIL import ImageTk, Image

DEBUG = 0
try:
    import pdb
except ImportError:
    DEBUG = 0


class Error(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg):
        self.msg = 'error: %s' % msg

    def print_error(self, msg):
        print(self.msg)


class DAgger(object):
    """
    """
    def __init__(self):
        pass
