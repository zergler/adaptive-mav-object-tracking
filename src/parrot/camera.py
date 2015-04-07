#!/usr/bin/env python2

import cv2
import threading


class CameraError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg):
        self.msg = 'Error: %s' % msg

    def print_error(self):
        print(self.msg)


class CameraInitError(CameraError):
    def __init__(self, arg):
        self.msg = 'Error: camera did not initialize succesfully.'


class CameraWindowError(CameraError):
    def __init__(self, arg):
        self.msg = 'Error: window parameters are invalid.'


class Camera(threading.Thread):
    """ Encapsulates the camera on the AR Parrot Drone 2.0.

        Handles the receiving of images from the drone using OpenCV. The way to
        interface with this method is to call get_image().
    """
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.address = address
        self.capturing = False

        error_image_filename = '../../samples/error_image.jpg'
        error_image = cv2.imread(error_image_filename)
        self.image = error_image

    def run(self):
        cap = cv2.VideoCapture(self.address)
        while cap.isOpened():
            self.capturing = True
            (ret, frame) = cap.read()
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if ret:
                self.image = image_rgb
            else:
                self.capturing = False
                cap.release()

    def get_image(self):
        return self.image

    @staticmethod
    def get_windows(image, window_size, percent_overlap):
        """ Gets the windows of the image.

            Descritizes the image into a bunch of cells with a size given by
            window_size, a 2-tuple specifying the size of the x and y
            descritizations. The percentage of each image which overlaps its
            neighbors (not counting the border cells) is given by
            percent_overlap. Ignores the borders.
        """
        # Check for errors in the passed parameters.
        if image is None:
            raise CameraWindowError()
        if window_size is None:
            raise CameraWindowError()
        elif len(window_size) != 2:
            raise CameraWindowError()
        if not (0 <= percent_overlap <= 3):
            raise CameraWindowError()

        # Get the size of the image.
        (y, x, d) = image.shape

        # Get the length of a non-overlapping bin.
        length = (x/window_size[0], y/window_size[1])
        overlap = (int(math.floor(length[0]*percent_overlap/4)), int(math.floor(length[1]*percent_overlap/4)))

        # Matrix that will hold the images.
        windows = [[None for z in range(0, window_size[0])] for z in range(0, window_size[1])]
        for r in range(0, window_size[1]):
            for c in range(0, window_size[0]):
                x_start = length[0]*(c) - overlap[0]
                x_end   = length[0]*(c + 1) + overlap[0]
                y_start = length[1]*(r) - overlap[1]
                y_end   = length[1]*(r + 1) + overlap[1]
                windows[r][c] = (x_start, x_end, y_start, y_end)

        return windows


def test_camera():
    """ Tests the camera module.
    """
    pdb.set_trace()
    # test_get_image()
    test_get_windows()


def test_get_image():
    try:
        camera_address = 'tcp://192.168.1.1:5555'
        camera = Camera(camera_address)
        camera.daemon = True
        camera.start()

        # Wait until the camera thread is initialized.
        timeout = time.time() + 15  # max wait is 15 seconds
        while True:
            if camera.capturing:
                break
            if time.time() > timeout and not camera.capturing:
                raise camera.CameraInitError()

        test_get_image(camera)

    except camera.CameraInitError as e:
        e.print_error()
        sys.exit(1)
    while true:
        cv2.imshow('image', camera.get_image())
        key = cv2.waitkey(1) & 0xff
        if key == ord('q'):
            break


def test_get_windows():
    test_image_filename = '../../samples/test_forest.jpg'
    test_image = cv2.imread(test_image_filename)

    x = 15
    y = 7
    overlap = 0.5
    windows = Camera.get_windows(test_image, (x, y), overlap)
    for r in range(0, y):
        for c in range(0, x):
            cv2.rectangle(test_image, (windows[r][c][0], windows[r][c][2]), (windows[r][c][1], windows[r][c][3]), (0, 0, 255), 2)
            cv2.imshow('Image window', test_image)
            cv2.waitKey(0)


if __name__ == '__main__':
    import math
    import pdb
    import sys
    import time
    test_camera()
