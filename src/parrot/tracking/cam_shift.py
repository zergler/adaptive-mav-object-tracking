#!/usr/bin/env python2.7

""" Cam shift object tracking.
"""

import numpy as np
import cv2
import bounding_box as bb


class CamShift(object):
    """ Cam shift algorithm.
    """
    def __init__(self, init_frame, vertex_1, vertex_2):
        # Grab the values from the vertices.
        c1 = vertex_1[0]
        r1 = vertex_1[1]
        c2 = vertex_2[0]
        r2 = vertex_2[1]
        h = abs(r1 - r2)
        w = abs(c1 - c2)
        r = min(r1, r2)
        c = min(c1, c2)

        # Setup initial location of window.
        self.track_window = (c, r, w, h)

        # Set up the ROI for tracking.
        roi = init_frame[r:r+h, c:c+w]
        hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        self.roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
        cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)

        # Setup the termination criteria, either 10 iteration or move by atleast 1 pt.
        self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

    def extract(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1)

        # Apply meanshift to get the new location.
        (ret, self.track_window) = cv2.CamShift(dst, self.track_window, self.term_crit)

        # Draw it on image.
        pts = np.int0(cv2.cv.BoxPoints(ret))
        cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
        # frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        return frame


def test_cam_shift(test_filename):
    # Get the video used for the test.
    stream = cv2.VideoCapture(test_filename)
    (ret, init_frame) = stream.read()
    clone_init_frame = init_frame.copy()

    # Get the bounding box from the user.
    box = bb.BoundingBox(init_frame)
    cv2.namedWindow("Test")
    cv2.setMouseCallback("Test", box.click_and_bound)

    # Display the image and wait for a keypress.
    while True:
        cv2.imshow("Test", init_frame)
        key = cv2.waitKey()
        bound = box.get_bounding_box()
        if box.get_bounding_box() is not None:
            cv2.rectangle(init_frame, bound[0], bound[1], (0, 0, 255), 2)
            cv2.imshow("Test", init_frame)

        # if the 'r' key is pressed, reset the cropping region.
        if key == ord("r"):
            init_frame = clone_init_frame.copy()

        if key == ord('q'):
            break

    cv2.destroyWindow('Test')
    bound = box.get_bounding_box()

    cam_shift = CamShift(init_frame, bound[0], bound[1])
    while stream.isOpened():
        (ret, frame) = stream.read()
        cv2.waitKey(0)
        if ret:
            cam_shift_frame = cam_shift.extract(frame)
            if cam_shift_frame is not None:
                cv2.imshow("frame", cam_shift_frame)
        else:
            stream.release()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.release()
    cv2.destroyAllWindows()


def main():
    test_filename = '../samples/test_nalgene.mov'
    test_cam_shift(test_filename)

if __name__ == '__main__':
    main()
