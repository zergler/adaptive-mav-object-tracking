#!/usr/bin/env python2

""" Debug module.
"""

class DebugError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg='', warning=False):
        default_header = 'Error: debug:'
        default_error = '%s an exception occured.' % default_header
        self.msg = default_error if msg == '' else '%s %s.' % (default_header, msg)
        self.warning = warning

    def print_error(self):
        print(self.msg)


class Debug(object):
    """ Prints out debug information and logs it if need be.
    """
    def __init__(self, verbosity):
        self.verbosity = verbosity

    def debug(self, msg, priority):
        if priority >= self.verbosity:
            print(msg)
