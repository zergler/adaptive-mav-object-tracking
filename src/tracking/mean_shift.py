#!/usr/bin/env python2.7

""" Mean shift object tracking.
"""

import pdb
import numpy as np
import cv2
import Tkinter as tk
from PIL import ImageTk, Image


class MeanShift(object):
    """ Mean shift object tracking.
    """
    def __init__(self, init_frame, vertex_1, vertex_2):
        # Grab the values from the vertices.
        r = vertex_1[0]
        c = vertex_1[1]
        h = abs(vertex_1[0] - vertex_2[0])
        w = abs(vertex_1[1] - vertex_2[1])

        # setup initial location of window
        self.track_window = (c, r, w, h)

        # set up the ROI for tracking
        roi = init_frame[r:r+h, c:c+w]
        hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        self.roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
        cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)

        # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
        self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

    def extract(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1)

        # apply meanshift to get the new location
        ret, self.track_window = cv2.meanShift(dst, self.track_window, self.term_crit)

        # Draw it on image
        x, y, w, h = self.track_window
        cv2.rectangle(frame, (x, y), (x+w, y+h), 255, 2)
        return frame


def test_mean_shift(test_filename):
    # Get the video used for the test.
    stream = cv2.VideoCapture(test_filename)
    (ret, init_frame) = stream.read()

    # # Usingthe first frame, draw a bounding box with mouse clicks.
    # root = tk.Tk()
    # vertex_frame = tk.Frame(root)
    # init_frame = cv2.cvtColor(init_frame, cv2.COLOR_BGR2RGB)
    # pil_frame = Image.fromarray(init_frame)

    # photo_frame = ImageTk.PhotoImage(pil_frame)
    # cam_label = tk.Label(vertex_frame, image=photo_frame)
    # cam_label.image = photo_frame
    # cam_label.pack()
    # root.mainloop()

    mean_shift = MeanShift(init_frame, (500, 500), (50, 50))
    while stream.isOpened():
        (ret, frame) = stream.read()
        if ret:
            mean_shift_frame = mean_shift.extract(frame)
            if mean_shift_frame is not None:
                cv2.imshow("frame", mean_shift_frame)
        else:
            stream.release()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.release()
    cv2.destroyAllWindows()


def main():
    test_filename = '../../samples/test_arizona2.mp4'
    test_mean_shift(test_filename)


if __name__ == '__main__':
    main()



