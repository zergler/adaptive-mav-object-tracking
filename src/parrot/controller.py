#!/usr/bin/env python2

import errno
import socket
import threading


class ControllerError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg):
        self.msg = 'Error: %s' % msg

    def print_error(self):
        print(self.msg)


class ControllerInitError(ControllerError):
    def __init__(self):
        self.msg = 'Error: controller did not initialize succesfully.'


class ControllerConnectionError(ControllerError):
    def __init__(self):
        self.msg = 'Error: connection to drone refused.'


class Controller(threading.Thread):
    """ Handles the sending of commands to the drone.
    """
    def __init__(self):
        threading.Thread.__init__(self, queue)
        self.queue = queue
        self.sps  # number of cmd sends per second (*not really*)

    def run(self):
        try:
            self.cmd_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cmd_soc.connect(('localhost', 9000))

            while True:
                cmd = queue.get()
                self.cmd_soc.send(cmd)

        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                ControllerConnectionError().print_error()
            if e[0] == errno.EPIPE:
                ControllerConnectionError().print_error()


def _test_controller():
    pdb.set_trace()

if __name__ == '__main__':
    import pdb
    _test_controller()
