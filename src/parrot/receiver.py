#!/usr/bin/env python2

import multiprocessing


class Receiver(multiprocessing.Process):
    """ Handles the receiving of navigation data from the drone.
    """
    def __init__(self, address):
        multiprocessing.Process.__init__(self)
        self.address = address


def test_receiver():
    pdb.set_trace()

if __name__ == '__main__':
    import pdb
    test_receiver()
