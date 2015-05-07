#!/usr/bin/env python2

""" Camera module.
"""

import cv2
import debug
import math
import threading
import Queue


class Camera(threading.Thread):
    """ Encapsulates the camera on the AR Parrot Drone 2.0. Handles the
        receiving of images from the drone using OpenCV.
    """
    def __init__(self, debug_queue, error_queue, address, queue):
        threading.Thread.__init__(self)
        self.debug_queue = debug_queue
        self.error_queue = error_queue
        self.address = address
        self.queue = queue

    def run(self):
        cap = self.get_cap()
        while cap.isOpened():
            (ret, frame) = cap.read()
            # If the image needs to converted to PIL, uncomment this line.
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if ret:
                try:
                    self.queue.put(frame, block=False)
                except Queue.Full:
                    pass
            else:
                cap.release()

    def get_cap(self):
        return cv2.VideoCapture(self.address)


def _test_camera():
    """ Tests the camera module.
    """
    pdb.set_trace()

    # Conduct tests...
    _test_get_image()
    #_test_get_windows(show_window=False)


def _test_get_image():
    # Set up debug.
    verbosity = 1
    error_queue = Queue.Queue()
    debug_queue = Queue.Queue()
    debugger = debug.Debug(verbosity, debug_queue, error_queue)

    # Make sure the images look right.
    image_queue = Queue.Queue(maxsize=1)
    camera_address = 'tcp://192.168.1.1:5555'
    camera = Camera(debug_queue, error_queue, camera_address, image_queue)
    camera.daemon = True
    camera.start()

    try:
        i = 0
        while True:
            debugger.debug()
            image = image_queue.get(block=True)
            cv2.imshow('image', image)
            key = cv2.waitKey(1) & 0xff
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite('image_%s.png' % str(i), image)
                i += 1
        debugger.debug()
    except debug.Error as e:
        e.print_error()
    except KeyboardInterrupt:
        sys.exit(0)


def _test_get_windows(show_window=False):
    # Make sure the resulting windows look right.
    test_image_filename = './../samples/test_forest.jpg'
    test_image = cv2.imread(test_image_filename)
    clone = test_image.copy()

    x = 10
    y = 5
    overlap = 0.25
    pdb.set_trace()
    windows = Camera.get_windows(test_image, (x, y), overlap)
    for r in range(0, y):
        for c in range(0, x):
            cur_window = clone[windows[r][c][2]:windows[r][c][3], windows[r][c][0]:windows[r][c][1]]
            cv2.rectangle(test_image, (windows[r][c][0], windows[r][c][2]), (windows[r][c][1], windows[r][c][3]), (0, 0, 255), 2)
            if show_window:
                cv2.imshow('Image window', cur_window)
                cv2.waitKey(0)
            else:
                cv2.imshow('Image', test_image)
                cv2.waitKey(0)


if __name__ == '__main__':
    import pdb
    import sys
    _test_camera()
