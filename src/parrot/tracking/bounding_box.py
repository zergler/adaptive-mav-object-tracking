#!/usr/bin/env python2.7

""" Lets the user draw a bounding box around an image for input into an image
    processing algorithm.
"""

import cv2


class BoundingBoxError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg):
        self.msg = 'Error: bounding box is invalid.'

    def print_error(self):
        print(self.msg)


class BoundingBox(object):
    """ Bounding box tool.
        Code credit: Adrian Rosebrock
        URL: http://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/
    """
    def __init__(self, image2bound):
        self.image2bound = image2bound
        self.ref = []
        self.active = False

    def click_and_bound(self, event, x, y, flags, param):
            # If the left mouse button was clicked, record the starting (x, y)
            # coordinates and indicate that the operation is active.
            if event == cv2.EVENT_LBUTTONDOWN:
                self.ref = [(x, y)]
                self.active = True

            # Check to see if the left mouse button was released.
            elif event == cv2.EVENT_LBUTTONUP:
                # Record the ending (x, y) coordinates and indicate that
                # the operation is complete.
                self.ref.append((x, y))
                self.cropping = False

    def get_bounding_box(self):
        if self.ref is not None:
            if len(self.ref) == 2:
                return self.ref
        return None


def _test_bounding_box():
    pdb.set_trace()
    test_filename = '../../../samples/test_nalgene.mov'

    # Get the video used for the test.
    stream = cv2.VideoCapture(test_filename)
    (ret, init_image) = stream.read()
    test_image = cv2.resize(init_image, (0, 0), fx=0.5, fy=0.5)
    bound_box = BoundingBox(test_image)

    clone = test_image.copy()
    cv2.namedWindow("Test of Bounding Box Tool")
    cv2.setMouseCallback("Test of Bounding Box Tool", bound_box.click_and_bound)

    while True:
            # Display the image and wait for a keypress.
            cv2.imshow("Test of Bounding Box Tool", test_image)
            key = cv2.waitKey(1) & 0xFF

            # Draw a rectangle around the region of interest.
            if bound_box.ref is not []:
                if len(bound_box.ref) == 2:
                    bb_test_image = test_image.copy()
                    cv2.rectangle(bb_test_image, bound_box.ref[0], bound_box.ref[1], (0, 255, 0), 2)
                    cv2.imshow("Test of Bounding Box Tool", bb_test_image)
                    key = cv2.waitKey(0)

            # if the 'r' key is pressed, reset the cropping region.
            if key == ord("r"):
                test_image = clone.copy()

            # if the 'q' key is pressed, break from the loop
            elif key == ord("q"):
                break

    # if there are two reference points, then crop the region of interest
    # from the image and display it
    # if len(bound_box.ref) == 2:
    #         roi = clone[bound_box.ref[0][1]:bound_box.ref[1][1], bound_box.ref[0][0]:bounx_box.ref[1][0]]
    #         cv2.imshow("ROI", roi)
    #         cv2.waitKey(0)

    # Close all open windows.
    cv2.destroyAllWindows()


if __name__ == '__main__':
    import pdb
    _test_bounding_box()
