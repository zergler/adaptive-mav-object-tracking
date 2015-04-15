#!/usr/bin/env python2

import errno
import json
import socket
import threading
import time


class ReceiverError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg='', warning=False):
        default_header = 'Error: receiver'
        default_error = '%s: an exception occured.' % default_header
        self.msg = default_error if msg == '' else '%s: %s.' % (default_header, msg)
        self.warning = warning

    def print_error(self):
        print(self.msg)


class Receiver(threading.Thread):
    """ Handles the receiving of navigation data from the drone.
    """
    def __init__(self, queue, bucket):
        threading.Thread.__init__(self)
        self.queue = queue
        self.bucket = bucket
        self.qps = 1  # number of queries per second (*not really*)
        self.bufsize = 8192

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
                self.bucket.put(ReceiverError('unable to connect to receiver server'))
            if e[0] == errno.EPIPE:
                self.bucket.put(ReceiverError('bad pipe to receiver server'))

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
            navdata = self.soc.recv(self.bufsize)
        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                self.bucket.put(ReceiverError('unable to connect to receiver server'))

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
