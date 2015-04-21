#!/usr/bin/env python2.7

""" Extracts hough transform features from the drone.
"""

import numpy as np
import cv2


class HoughTransform(object):
    """ Extracts Hough transform features.
    """
    def __init__(self):
        # Parameters for the Hough transform.
        self.min_line_length = 100  # max length of each line in pixels
        self.max_line_gap = 5       # max gap between lines in pixels
        self.rho = 1                # distance resolution of the accumulator in pixels
        self.theta = np.pi/180.0    # angle resolution of the accumulator in radians
        self.hough_thresh = 100     # accumulator threshold parameter in number of votes

        # The maximum angled allowed for a line to be valid when the line is
        # intersected with a vertical line. Setting this parameter to pi allows
        # all lines to be valid while setting it to 0 (+ delta) allows only
        # vertical lines to be valid.
        self.phi = np.pi

        # Parameters for the Canny edge detector.
        self.can_thresh1 = 50
        self.can_thresh2 = 100
        self.aperature_size = 3

    def extract(self, img):
        """ Applies the Hough transform to the image to find lines in it.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, self.can_thresh1, self.can_thresh2, apertureSize=self.aperature_size)
        lines = cv2.HoughLinesP(edges, self.rho, self.theta, self.hough_thresh, self.min_line_length, self.max_line_gap)
        return lines

    @staticmethod
    def get_image(img, lines):
        """ Draws the lines found by Hough transform extractor on the image.
        """
        for x1, y1, x2, y2 in lines[0]:
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return img

    @staticmethod
    def get_features(lines):
        """ Computes features from the lines found by the Hough transform
            extractor.
        """
        # Get the top line.
        if lines is not None:
            feats = np.array(lines[0][0:1])
            feats = np.transpose(feats)
        else:
            feats = np.zeros((4, 1))
        return feats


def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def _test_hough_transform():
    pdb.set_trace()
    test_filename = './../../samples/test_hough.jpg'

    image = cv2.imread(test_filename, cv2.CV_LOAD_IMAGE_COLOR)
    hough_transform = HoughTransform()
    lines = hough_transform.extract(image)
    image = HoughTransform.get_image(image, lines)
    feats = HoughTransform.get_features(lines)
    cv2.imshow('Hough Lines on Test Forest Image', img)
    cv2.waitKey()


if __name__ == '__main__':
    import pdb
    _test_hough_transform()
