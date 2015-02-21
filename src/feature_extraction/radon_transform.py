#!/usr/bin/env python2.7

""" Extracts radon transform features from the drone.
"""

import numpy as np
import cv2


class RadonTransform(object):
    """ Radon transform features.
    """
    def __init__(self):
        pass

    def extract(self, img):
        pass


def test_radon_transform(object):
    sample_imgs = [None]
    radon_transform = RadonTransform()
    radon_transform.extract(sample_imgs[0])

if __name__ == '__main__':
    test_radon_transform()
