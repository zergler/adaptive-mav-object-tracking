#!/usr/bin/env python2

""" Contains useful functions for training.
"""

import cv2
import math


def annotate_input(image, cmd, invert=False):
    """ Annotates the image with a line for the left/right and up/down inputs.
    """
    vert = cmd['Y'] if invert else -cmd['Y']
    horz = cmd['X']
    shape = image.shape

    x_1 = [shape[1]/2, 0]
    x_2 = [shape[1]/2, shape[0]]
    y_1 = [0, shape[0]/2]
    y_2 = [shape[1], shape[0]/2]

    x_1[0] += int(math.floor(horz*shape[1]/2))
    x_2[0] += int(math.floor(horz*shape[1]/2))
    y_1[1] += int(math.floor(vert*shape[0]/2))
    y_2[1] += int(math.floor(vert*shape[0]/2))

    cv2.line(image, tuple(x_1), tuple(x_2), (255, 0, 0), 2)
    cv2.line(image, tuple(y_1), tuple(y_2), (0, 0, 255), 2)
    return image


def _test_annotate_input():
    pdb.set_trace()
    test_filename = '../../samples/test_forest.jpg'
    test_image = cv2.imread(test_filename)
    test_cmd = {
        'X': -0.9,
        'Y': -0.9,
        'Z': 0.0,
        'R': 0.0,
        'C': 0,
        'T': False,
        'L': False,
        'S': False
    }
    annotated_image = annotate_input(test_image, test_cmd)
    cv2.imshow('Annotated Image', annotated_image)
    cv2.waitKey(0)

if __name__ == '__main__':
    import pdb
    _test_annotate_input()
