#!/usr/bin/env python2

""" Contains useful functions for training.
"""

import cv2
import math


def annotate(image, cmd_drone, cmd_expert, invert=False):
    """ Annotates the image with a line for the left/right and up/down inputs.
    """
    image = _annotate(image, cmd_drone, (255, 0, 0), invert)
    image = _annotate(image, cmd_expert, (0, 0, 255), invert)
    return image


def _annotate(image, cmd, color, invert=False):
    # Update
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

    cv2.line(image, tuple(x_1), tuple(x_2), color, 2)
    cv2.line(image, tuple(y_1), tuple(y_2), color, 2)
    return image


def _test_annotate_input():
    pdb.set_trace()
    test_filename = '../../samples/test_forest.jpg'
    test_image = cv2.imread(test_filename)
    test_cmd_drone = {
        'X': -0.5,
        'Y': -0.4,
        'Z': 0.0,
        'R': 0.0,
        'C': 0,
        'T': False,
        'L': False,
        'S': False
    }
    test_cmd_expert = {
        'X': -0.3,
        'Y': -0.2,
        'Z': 0.0,
        'R': 0.0,
        'C': 0,
        'T': False,
        'L': False,
        'S': False
    }
    annotated_image = annotate(test_image, test_cmd_drone, test_cmd_expert)
    cv2.imshow('Annotated Image', annotated_image)
    cv2.waitKey(0) & 0xFF
    pdb.set_trace()

if __name__ == '__main__':
    import pdb
    _test_annotate_input()
