#!/usr/bin/env python2

import cv2
import math
import threading
import Queue


class ReceiverError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg='', warning=False):
        default_header = 'Error: camera'
        default_error = '%s: an exception occured.' % default_header
        self.msg = default_error if msg == '' else '%s: %s.' % (default_header, msg)
        self.warning = warning

    def print_error(self):
        print(self.msg)


class Camera(threading.Thread):
    """ Encapsulates the camera on the AR Parrot Drone 2.0. Handles the
        receiving of images from the drone using OpenCV.
    """
    def __init__(self, address, queue, bucket):
        threading.Thread.__init__(self)
        self.address = address
        self.queue = queue
        self.bucket = bucket

    def run(self):
        cap = cv2.VideoCapture(self.address)
        while cap.isOpened():
            (ret, frame) = cap.read()
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if ret:
                try:
                    self.queue.put(image_rgb, block=False)
                except Queue.Full:
                    pass
            else:
                cap.release()

    @staticmethod
    def get_windows(image, window_size, percent_overlap):
        """ Gets the windows of the image.

            Descritizes the image into a bunch of cells with a size given by
            window_size, a 2-tuple specifying the size of the x and y
            descritizations. The percentage of each image which overlaps its
            neighbors is given by percent_overlap.
        """
        (y, x, d) = image.shape
        length = (x/window_size[0], y/window_size[1])
        overlap = (int(math.floor(length[0]*percent_overlap/4)), int(math.floor(length[1]*percent_overlap/4)))

        # Matrix that will hold the window sizes.
        windows = [[None for z in range(0, window_size[0])] for z in range(0, window_size[1])]
        for r in range(0, window_size[1]):
            for c in range(0, window_size[0]):
                x_start = length[0]*(c) - overlap[0]
                x_end   = length[0]*(c + 1) + overlap[0]
                y_start = length[1]*(r) - overlap[1]
                y_end   = length[1]*(r + 1) + overlap[1]
                windows[r][c] = (x_start, x_end, y_start, y_end)

        windows = [[tuple(j if j > 0 else 0 for j in i) for i in k] for k in windows]  # remove bad (negative) values
        return windows


def _test_camera():
    """ Tests the camera module.
    """
    pdb.set_trace()

    # Conduct tests...
    # _test_get_image()
    _test_get_windows()


def _test_get_image():
    # Make sure the images look right.
    image_queue = Queue.Queue()
    camera_address = 'tcp://192.168.1.1:5555'
    camera = Camera(camera_address, image_queue)
    camera.daemon = True
    camera.start()

    while True:
        cv2.imshow('image', image_queue.get())
        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            break


def _test_get_windows():
    # Make sure the resulting windows look right.
    test_image_filename = '../../samples/test_forest.jpg'
    test_image = cv2.imread(test_image_filename)

    x = 15
    y = 7
    overlap = 0.5
    pdb.set_trace()
    windows = Camera.get_windows(test_image, (x, y), overlap)
    for r in range(0, y):
        for c in range(0, x):
            cur_window = test_image[windows[r][c][2]:windows[r][c][3], windows[r][c][0]:windows[r][c][1]]
            cv2.rectangle(test_image, (windows[r][c][0], windows[r][c][2]), (windows[r][c][1], windows[r][c][3]), (0, 0, 255), 2)
            cv2.imshow('Image window', cur_window)
            cv2.waitKey(0)


if __name__ == '__main__':
    import pdb
    _test_camera()
