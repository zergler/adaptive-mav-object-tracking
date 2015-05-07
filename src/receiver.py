#!/usr/bin/env python2

""" Receiver module.
"""

import debug
import errno
import json
import socket
import threading
import time


class Receiver(object):
    """ Handles the receiving of navigation data from the drone.
    """
    def __init__(self, debug_queue, error_queue):
        self.debug_queue = debug_queue
        self.error_queue = error_queue
        self.bufsize = 8192

        query = {
            'N': True
        }
        self.query_json = json.dumps(query)


        try:
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.connect(('localhost', 9001))
            self.soc.setblocking(1)
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
        self.soc.send(self.query_json)
        try:
            navdata = self.soc.recv(self.bufsize)
        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                self.error_queue.put(debug.Error('receiver', 'unable to connect to receiver server'))
        return navdata

    def get_navdata(self):
        time.sleep(0.1)
        navdata_json = self.recv_navdata()
        navdata = json.loads(navdata_json)
        return navdata

def _test_receiver():
    pdb.set_trace()

    # Set up debug.
    verbosity = 1
    error_queue = Queue.Queue()
    debug_queue = Queue.Queue()
    debugger = debug.Debug(verbosity, debug_queue, error_queue)

    # Set up receiver.
    receiver = Receiver(debug_queue, error_queue)

    try:
        while True:
            debugger.debug()
            navdata = receiver.get_navdata()
            pprint.pprint(navdata)
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
