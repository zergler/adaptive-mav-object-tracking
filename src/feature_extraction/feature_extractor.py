#!/usr/bin/env python2.7

""" Feature extractor which extracts features in a thread.
"""

import math
import threading
import Queue
import cv2
import numpy as np

# Feature modules.
import hough_transform
import optical_flow
import laws_mask
import history


class FeatureExtractor(object):
    def __init__(self, feature_queue, init_image, window_size, overlap, cmd_history_feats, cmd_history_length, nav_history_feats, nav_history_length):
        self.feature_queue = feature_queue
        self.init_image = init_image
        self.window_size = window_size
        self.overlap = overlap
        self.cmd_history_feats = cmd_history_feats
        self.cmd_history_length = cmd_history_length
        self.nav_history_feats = nav_history_feats
        self.nav_history_length = nav_history_length
        self.init_feature_extract()

    def extract(self, image):
        t = threading.Thread(target=self.get_features, args=(image,))
        t.start()

    def update(self, cmd, navdata):
        self.extractor_nav_history.update(navdata)
        self.extractor_cmd_history.update(cmd)

    def init_feature_extract(self):
        # Grab an example window from the initial image to feed the optical flow
        # feature extractor (use a non border window).
        windows = get_windows(self.init_image, self.window_size, self.overlap)
        small_image = self.init_image[windows[1][1][2]:windows[1][1][3], windows[1][1][0]:windows[1][1][1]]

        # Initialize each feature extractor.
        self.extractor_opt_flow = optical_flow.OpticalFlow(small_image)
        self.extractor_hough_trans = hough_transform.HoughTransform()
        self.extractor_laws_mask = laws_mask.LawsMask()
        self.extractor_cmd_history = history.CmdHistory(self.cmd_history_feats, self.cmd_history_length)
        self.extractor_nav_history = history.NavHistory(self.nav_history_feats, self.nav_history_length)

    def get_visual_features(self, image):
        # Get the windows from the current image.
        windows = get_windows(image, self.window_size, self.overlap)

        # Arrays that will contain the different features.
        feats_all = np.array([])
        feats_flow = np.array([])
        feats_hough = np.array([])
        feats_laws = np.array([])

        # Iterate through the windows, computing features for each.
        for r in range(0, self.window_size[1]):
            for c in range(0, self.window_size[0]):
                # Get the current window of the image for which the features
                # will be extracted from.
                cur_window = image[windows[r][c][2]:windows[r][c][3], windows[r][c][0]:windows[r][c][1]]

                # If the current window is a border window, it may have a
                # smaller size, so reshape it.
                cur_window = cv2.resize(cur_window, self.extractor_opt_flow.shape[::-1])

                # Get the optical flow features from the current window.
                flow = self.extractor_opt_flow.extract(cur_window)
                feats_cur = optical_flow.OpticalFlow.get_features(flow)
                feats_flow = np.vstack((feats_flow, feats_cur)) if feats_flow.size else feats_cur

                # Get the Hough transform features from the current window.
                lines = self.extractor_hough_trans.extract(cur_window)
                feats_cur = hough_transform.HoughTransform.get_features(lines)
                feats_hough = np.vstack((feats_hough, feats_cur)) if feats_hough.size else feats_cur

                # Get the Law's texture mask features from the current window.
                feats_cur = self.extractor_laws_mask.extract(cur_window)
                feats_laws = np.vstack((feats_laws, feats_cur)) if feats_laws.size else feats_cur

        # Vertically stack all of the different features.
        feats_all = np.vstack((feats_all, feats_flow)) if feats_all.size else feats_flow
        feats_all = np.vstack((feats_all, feats_hough)) if feats_all.size else feats_hough
        feats_all = np.vstack((feats_all, feats_laws)) if feats_all.size else feats_laws

        # Transpose and return.
        return np.transpose(feats_all)

    def get_nav_features(self):
        # Get the command and navigation data history features.
        feats_cmd_history = self.extractor_cmd_history.extract()
        feats_nav_history = self.extractor_nav_history.extract()
        feats_all = np.vstack((feats_cmd_history, feats_nav_history))
        return np.transpose(feats_all)

    def get_features(self, image):
        visual_features = self.get_visual_features(image)
        nav_features = self.get_nav_features()
        feats = np.hstack((visual_features, nav_features))
        self.feature_queue.put(feats)


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


def _test_feature_extractor():
    pdb.set_trace()

    feature_queue = Queue.Queue(maxsize=1)
    init_image = cv2.imread('../samples/test_forest.jpg')
    window_size = (10, 5)
    overlap = 0.25
    cmd_history_feats = 7    # the approximate number of cmd history features
    cmd_history_length = 10  # keep a running list of the last 10 cmds
    nav_history_feats = 7    # the approximate number of nav history features
    nav_history_length = 10  # keep a running list of the last 10 nav data

    fe = FeatureExtractor(feature_queue,
                          init_image,
                          window_size,
                          overlap,
                          cmd_history_feats,
                          cmd_history_length,
                          nav_history_feats,
                          nav_history_length)
    
    pdb.set_trace()
    fe.extract(init_image, '', '')

    while True:
        blah = None
        try:
            blah = feature_queue.get(block=False)
        except Queue.Empty:
            pass
        if blah is not None:
            break

    print('Success.')

if __name__ == '__main__':
    import pdb
    _test_feature_extractor()
