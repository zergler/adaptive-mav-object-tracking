#!/usr/bin/env python2

import errno
import socket
import threading


class Error(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg):
        self.msg = 'Error: %s' % msg

    def print_error(self):
        print(self.msg)


class ConnectionError(Error):
    def __init__(self):
        self.msg = 'Error: connection to drone refused.'


class Controller(threading.Thread):
    """ Handles the sending of commands to the drone.
    """
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # Connect to the node js server.
        # subprocess.call(['./parrot_server.js', ''])
        try:
            self.cmd_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cmd_soc.connect(('localhost', 9000))
        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                ConnectionError().print_error()

    def send_cmd(self, cmd):
        try:
            self.cmd_soc.send(cmd)
        except socket.error as e:
            if e[0] == errno.EPIPE:
                ConnectionError().print_error()


def test_controller():
    pdb.set_trace()

if __name__ == '__main__':
    import pdb
    test_controller()
