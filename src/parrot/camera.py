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

    def get_windows(self, image, window_size, percent_overlap):
        """ Gets the windows of the image.

            Descritizes the image into a bunch of cells with a size given by
            window_size, a 2-tuple specifying the size of the x and y
            descritizations. The percentage of each image which overlaps its
            neighbors (not counting the border cells) is given by
            percent_overlap.
        """
        # Check for errors in the passed parameters.


def test_camera():
    """ Tests the camera module.
    """
    pdb.set_trace()
    camera_address = 'tcp://192.168.1.1:5555'
    camera = Camera(camera_address)
    camera.daemon = True
    camera.start()

    while True:
        cv2.imshow('Image', camera.get_image())
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

if __name__ == '__main__':
    import pdb
    test_camera()
