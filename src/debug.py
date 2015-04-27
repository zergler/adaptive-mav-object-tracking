#!/usr/bin/env python2

""" Debug module.
"""

import Queue
import signal
from contextlib import contextmanager


class Error(Exception):
    """ Eception class for the module.
    """
    def __init__(self, module, msg='', warning=False):
        header = 'Error: %s:' % module
        default_msg = '%s an exception occured.' % header
        self.msg = default_msg if msg == '' else '%s %s.' % (header, msg)
        self.warning = warning

    def print_error(self):
        print(self.msg)


@contextmanager
def time_limit(seconds):
    """ Code credit: Josh Lee
        http://stackoverflow.com/questions/366682/how-to-limit-execution-time-of
        -a-function-call-in-python
    """
    def signal_handler(signum, frame):
        raise Error('time:' 'function timed out')
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


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
