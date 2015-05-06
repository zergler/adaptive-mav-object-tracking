#!/usr/bin/env python2

""" Receiver module.
"""

import debug
import errno
import json
import socket
import threading
import time


class Receiver(threading.Thread):
    """ Handles the receiving of navigation data from the drone.
    """
    def __init__(self, debug_queue, error_queue, queue, qps):
        threading.Thread.__init__(self)
        self.debug_queue = debug_queue
        self.error_queue = error_queue
        self.queue = queue
        self.qps = qps  # number of queries per second (*not really*)
        self.bufsize = 8192

    def run(self):
        try:
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.connect(('localhost', 9001))
            self.soc.setblocking(0)

            # Only send queries every onece in a while.
            while True:
                time.sleep(1.0/self.qps)
                self.recv_navdata()
        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                self.error_queue.put(debug.Error('receiver', 'unable to connect to receiver server'))
            if e[0] == errno.EPIPE:
                self.error_queue.put(debug.Error('receiver', 'bad pipe to receiver server'))

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
                self.error_queue.put(debug.Error('receiver', 'unable to connect to receiver server'))

        # We only care about the most recent navdata so remove the outdated
        # data from the queue.
        if not self.queue.empty():
            self.queue.get()
        if navdata is not None:
            self.queue.put(navdata)


def _test_receiver():
    pdb.set_trace()

    # Set up debug.
    verbosity = 1
    error_queue = Queue.Queue()
    debug_queue = Queue.Queue()
    debugger = debug.Debug(verbosity, debug_queue, error_queue)

    # Set up receiver.
    qps = 0.5
    recv_queue = Queue.Queue(maxsize=1)
    receiver = Receiver(debug_queue, error_queue, recv_queue, qps)
    receiver.daemon = True
    receiver.start()

    try:
        while True:
            debugger.debug()
            try:
                navdata = recv_queue.get(block=False)
                navdata = json.loads(navdata)
                pprint.pprint(navdata)
                navdata = None
            except Queue.Empty:
                pass
    except debug.Error as e:
        e.print_error()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    import pdb
    import pprint
    import sys
    import Queue
    _test_receiver()
