#!/usr/bin/env python2

import errno
import json
import socket
import threading
import time


class ReceiverError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg):
        self.msg = 'Error: %s' % msg

    def print_error(self):
        print(self.msg)


class ReceiverInitError(ReceiverError):
    def __init__(self):
        self.msg = 'Error: receiver did not initialize succesfully.'


class ReceiverConnectionError(ReceiverError):
    def __init__(self):
        self.msg = 'Error: connection to drone refused.'


class Receiver(threading.Thread):
    """ Handles the receiving of navigation data from the drone.
    """
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.qps = 1  # number of queries per second (*not really*)
        self.bufsize = 4096

    def run(self):
        try:
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.connect(('localhost', 9001))
            self.soc.setblocking(0)

            # Only send queries every onece in a while.
            while True:
                time.sleep(float(1/self.qps))
                self.recv_navdata()
        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                ReceiverConnectionError().print_error()
            if e[0] == errno.EPIPE:
                ReceiverConnectionError().print_error()

    def recv_navdata(self):
        """ Gets the navigation data from the parrot by first sending a 'GET'
            query and then receiving the data.
        """
        navdata = None
        query = {
            'N': True
        }
        query = json.dumps(query)
        self.soc.send(query)
        try:
            navdata = self.soc.recv(8192)
        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                ReceiverConnectionError().print_error()

        # We only care about the most recent navdata so remove the outdated
        # data from the queue.
        if not self.queue.empty():
            self.queue.get()
        if navdata is not None:
            self.queue.put(navdata)


def _test_receiver():
    recv_queue = Queue.Queue()
    receiver = Receiver(recv_queue)
    receiver.daemon = True
    receiver.start()

    while True:
        navdata = recv_queue.get()
        navdata = json.loads(navdata)
        print(navdata['header'])



if __name__ == '__main__':
    # import pdb
    import Queue
    _test_receiver()
