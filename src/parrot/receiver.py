#!/usr/bin/env python2

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


class ReceiverConnectionError(receiverError):
    def __init__(self):
        self.msg = 'Error: connection to drone refused.'


class Receiver(threading.Thread):
    """ Handles the receiving of navigation data from the drone.
    """
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.qps = 2  # number of queries per second (*not really*)
        self.bufsize = 4096

    def run(self):
        try:
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.connect(('localhost', 9001))
            self.soc.setblocking(0)

            # Only send queries every onece in a while.
            while True:
                time.wait(float(1/self.qps))
                self.recv_navdata()
        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                ReceiverConnectionError().print_error()
            if e[0] == errno.EPIPE:
                ReceiverConnectionError().print_error()

    def recv_navdata(self):
        """ Gets the navigation data from the parrot by first sending a 'GET'
            query and then receiving the data. Times out after a while if no
            data is received.

            Code credit: John Nielsen
            http://code.activestate.com/recipes/408859-socketrecv-three-ways-to-turn-it-into-recvall/
        """
        query = json.dumps('GET')
        self.cmd_soc.send(query)

        total_data = []
        data = ''
        begin = time.time()
        while True:
            # If you got some data, then break after wait sec.
            if total_data and ((time.time() - begin) > timeout):
                break

            # If you got no data at all, wait a little longer.
            elif time.time() - begin > timeout*2:
                break
            data = the_socket.recv(self.bufsize)
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        navdata = ''.join(total_data)

        # We only care about the most recent navdata so remove the outdated
        # data from the queue.
        if not self.queue.empty():
            self.queue.get()
        self.queue.put(navdata)


def _test_receiver():
    pdb.set_trace()

if __name__ == '__main__':
    import pdb
    _test_receiver()
