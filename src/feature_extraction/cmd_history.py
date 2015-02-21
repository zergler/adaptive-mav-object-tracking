#!/usr/bin/env python2.7

""" Extracts command history features from the drone.
"""

import numpy as np
import cv2


class CmdHistory(object):
    """ Command history features.
    """
    def __init__(self):
        pass

    def extract(self, img):
        pass


def test_cmd_history(object):
    sample_imgs = [None]
    cmd_history = CmdHistory()
    cmd_history.extract(sample_imgs[0])

if __name__ == '__main__':
    test_cmd_history()
