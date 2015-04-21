#!/usr/bin/env python2

import errno
import socket
import threading


class ControllerError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg='', warning=False):
        default_header = 'Error: controller'
        default_error = '%s: an exception occured.' % default_header
        self.msg = default_error if msg == '' else '%s: %s.' % (default_header, msg)
        self.warning = warning

    def print_error(self):
        print(self.msg)


class Controller(threading.Thread):
    """ Handles the sending of commands to the drone.
    """
    def __init__(self, queue, bucket):
        threading.Thread.__init__(self)
        self.queue = queue
        self.bucket = bucket

    def run(self):
        try:
            self.cmd_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cmd_soc.connect(('localhost', 9000))

            while True:
                cmd = self.queue.get()
                self.cmd_soc.send(cmd)

        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                self.bucket.put(ControllerError('unable to connect to command server'))
            if e[0] == errno.EPIPE:
                self.bucket.put(ControllerError('bad pipe to command server'))


def _test_controller():
    pdb.set_trace()

    cmd_queue = Queue.Queue()
    controller = Controller(cmd_queue)
    controller.daemon = True
    controller.start()

    cmd_default = {
        'X': 0.0,
        'Y': 0.0,
        'R': 0.0,
        'C': 0,
        'T': False,
        'L': False,
        'S': False
    }
    cmd = cmd_default.copy()
    cmd['T'] = True
    cmd_json = json.dumps(cmd)
    cmd_queue.put(cmd_json)

    time.sleep(2)

    cmd = cmd_default.copy()
    cmd['L'] = True
    cmd_json = json.dumps(cmd)
    cmd_queue.put(cmd_json)


if __name__ == '__main__':
    import pdb
    import json
    import time
    import Queue
    _test_controller()
