#!/usr/bin/env python2.7

""" Extracts Law's mask features from the drone.
"""

import numpy as np
import cv2


class LawsMask(object):
    """ Law's Mask features.
    """
    def __init__(self):
        pass

    def extract(self, img):
        pass


def test_laws_mask(object):
    sample_imgs = [None]
    laws_mask = LawsMask()
    laws_mask.extract(sample_imgs[0])

if __name__ == '__main__':
    test_laws_mask()
