#!/usr/bin/env python2.7

""" Extracts the radon transform features from the drone.
"""

import traceback
import numpy as np
import cv2
from skimage.io import imread
from skimage import data_dir
from skimage.transform import radon, rescale


class RadonTransform(object):
    """ Extracts radon transform features.
    """
    def __init__(self, image):
        self.theta = np.linspace(0.0, 180.0, max(image.shape), endpoint=False)
        
    def extract(self, image):
        """ Applies the radon transform to the image.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        try:
            sinogram = radon(gray, theta=self.theta, circle=False)
        except:
            print(traceback.format_exc())
        return sinogram

    @staticmethod
    def get_features(sinogram):
        """ Computes features from the sinogram found by the radon transform
            extractor.
        """
        # Descritize the matrix into 15 by 15 bins.


def _test_radon_transform():
    pdb.set_trace()
    test_filename = './../../samples/test_forest.jpg'

    image = cv2.imread(test_filename, cv2.CV_LOAD_IMAGE_COLOR)
    radon_transform = RadonTransform(image)
    sinogram = radon_transform.extract(image)


if __name__ == '__main__':
    import pdb
    _test_radon_transform()
