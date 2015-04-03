#!/usr/bin/env python2.7

""" Extracts hough transform features from the drone.
"""

import pdb
import numpy as np
import cv2
import time
import pdb


class HoughTransform(object):
    """ hough transform features.
    """
    def __init__(self):
        pass

    def extract(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 100, apertureSize=3)
        #cv2.imshow('Hofsdjfosd', edges)
        #cv2.waitKey()
        minLineLength = 100
        maxLineGap = 5
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength, maxLineGap)
        for x1, y1, x2, y2 in lines[0]:
            if abs(float(float(x2) - float(x1))) < 0.1:
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return img


def test_hough_transform(test_filename):
    img = cv2.imread(test_filename, cv2.CV_LOAD_IMAGE_COLOR)
    hough_transform = HoughTransform()
    hough_transform.extract(img)
    cv2.imshow('Hough Lines on Test Forest Image', img)
    cv2.waitKey()


def main():
    test_image = '../../samples/test_hough.jpg'
    test_hough_transform(test_image)


if __name__ == '__main__':
    main()
