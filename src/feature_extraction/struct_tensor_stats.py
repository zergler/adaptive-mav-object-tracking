#!/usr/bin/env python2.7

""" Extracts struct tensor statistics features from the drone.
"""

import numpy as np
import cv2


class StructTensorStats(object):
    """ Struct tensor statistics features.
    """
    def __init__(self):
        pass

    def extract(self, img):
        pass


def test_struct_tensor_stats():
    sample_imgs = [None]
    struct_tensor_stats = StructTensorStats()
    struct_tensor_stats.extract(sample_imgs[0])

if __name__ == '__main__':
    test_struct_tensor_stats()
