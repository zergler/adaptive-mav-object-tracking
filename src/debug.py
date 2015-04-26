#!/usr/bin/env python2

""" Debug module.
"""

import Queue


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
    def __init__(self, verbosity, debug_queue, error_queue):
        self.verbosity = verbosity
        self.debug_queue = debug_queue
        self.error_queue = error_queue

    def debug(self):
        # Get all the messages in the queue and print them out.
        while True: 
            msg = None
            try:
                msg = self.debug_queue.get(block=False)
                if msg is not None:
                    if msg['PRIORITY'] >= self.verbosity:
                        print(msg['MSG'])
            except Queue.Empty:
                break

        # Get all messages in the error queue and print them out.
        while True:
            error = None 
            try:
                error = self.error_queue.get(block=False)
                if error is not None:
                    raise error
            except Queue.Empty:
                break

