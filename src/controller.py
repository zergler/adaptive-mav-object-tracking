#!/usr/bin/env python2

import debug
import errno
import socket
import threading


class Controller(threading.Thread):
    """ Handles the sending of commands to the drone.
    """
    def __init__(self, debug_queue, error_queue, queue):
        threading.Thread.__init__(self)
        self.debug_queue = debug_queue
        self.error_queue = error_queue
        self.queue = queue

    def run(self):
        try:
            self.cmd_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cmd_soc.connect(('localhost', 9000))

            while True:
                cmd = self.queue.get()
                self.cmd_soc.send(cmd)

        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                self.error_queue.put(debug.Error('controller', 'unable to connect to command server'))
            if e[0] == errno.EPIPE:
                self.error_queue.put(ControllerError('controller', 'bad pipe to command server'))


def _test_controller():
    pdb.set_trace()

    # Set up debug.
    verbosity = 1
    error_queue = Queue.Queue()
    debug_queue = Queue.Queue()
    debugger = debug.Debug(verbosity, debug_queue, error_queue)

    # Set up controller
    cmd_queue = Queue.Queue()
    controller = Controller(debug_queue, error_queue, cmd_queue)
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
