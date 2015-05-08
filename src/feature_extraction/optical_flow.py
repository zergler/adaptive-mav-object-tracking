#!/usr/bin/env python2.7

""" Extracts optical flow features from the drone.
"""

import numpy as np
import cv2


class OpticalFlow(object):
    """ Extracts dense optical flow features from an image and its predecessor
        using the Farneback method.

        Source: [Gunnar Farneback, Two-frame motion estimation based on
        polynomial expansion, Lecture Notes in Computer Science, 2003, (2749),
        363-370.]

        To Do: Implement optical flow with non-local total variation
        regularization to account for poorly textured regions, occlusions and
        small scale image structures.

        Source: [M. Werlberger, T. Pock, and H. Bischof. Motion estimation with
        non-local total variation regularization. In CVPR, 2010.]
    """
    def __init__(self, init_frame):
        # Parameters of the camera/images.
        (r, c, _) = init_frame.shape
        self.shape = (r, c)
        self.prev_gray = cv2.cvtColor(init_frame, cv2.COLOR_BGR2GRAY)

        # Parameters for farneback optical flow.
        self.pyr_scale = 0.5   # next layer is twice smaller than the previous
        self.levels = 5        # number of pyramid layers including the initial image
        self.winsize = 13      # averaging window size
        self.iterations = 10   # number of iterations at each pyramid level
        self.poly_n = 5        # size of the pixel neighborhood used to find polynomial expansion in each pixel
        self.poly_sigma = 1.1  # standard deviation of the Gaussian used to smooth derivatives used as a basis for the polynomial expansion
        self.flags = 0         # no flags (OPTFLOW_USE_INITIAL_FLOW, OPTFLOW_FARNEBACK_GAUSSIAN)

    def extract(self, frame):
        """ Extract optical flow from the current frame containing the
            cartesian flow vectors for each pixel.
        """
        # Get the cv flow using farneback
        cur_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(self.prev_gray,
                                            cur_gray,
                                            pyr_scale=self.pyr_scale,
                                            levels=self.levels,
                                            winsize=self.winsize,
                                            iterations=self.iterations,
                                            poly_n=self.poly_n,
                                            poly_sigma=self.poly_sigma,
                                            flags=self.flags)
        self.prev_gray = cur_gray
        return flow

    @staticmethod
    def get_image(flow):
        """ Extracts a viewable image from the flow matrix.
        """
        # Convert the flow to polar and normalize.
        (mag, ang) = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        (r, c, _) = flow.shape
        hsv = np.zeros((r, c, 3), dtype=np.uint8)
        hsv[..., 0] = ang*180/np.pi/2
        hsv[..., 1] = 255
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)

        # Get the color image and return it.
        flow_frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        return flow_frame

    @staticmethod
    def get_features(flow):
        """ Extracts the features from the flow matrix. Features extracted
            include:

            1. Minimum magnitude of flow.
            2. Maximum magnitude of flow.
            3. Mean magnitude of flow.
            4. Standard deviation of x flow.
            5. Standard deviation of y flow.
        """
        # Initialize feature vector.
        features = np.zeros((5, 1))
        indices = {
            'MIN':  0,
            'MAX':  1,
            'MEAN': 2,
            'STDX': 3,
            'STDY': 4
        }

        # Convert the flow to polar.
        flow_x = flow[..., 0]
        flow_y = flow[..., 1]
        (flow_mag, flow_ang) = cv2.cartToPolar(flow_x, flow_y)

        # Calculate the features.
        features[indices['MIN']] = np.min(flow_mag)
        features[indices['MAX']] = np.max(flow_mag)
        features[indices['MEAN']] = np.mean(flow_mag)
        features[indices['STDX']] = np.std(flow_x)
        features[indices['STDY']] = np.std(flow_y)
        return features


def _test_optical_flow():
    pdb.set_trace()
    test_filename = './../samples/test_cat.mp4'

    # Get the video used for the test.
    stream = cv2.VideoCapture(test_filename)
    (ret, init_frame) = stream.read()
    opt_flow = OpticalFlow(init_frame)

    # Conduct tests...
    # _test_optical_flow_extract(stream, opt_flow)
    _test_optical_flow_get_image(stream, opt_flow)
    # _test_optical_flow_get_features(stream, opt_flow)


def _test_optical_flow_extract(stream, opt_flow):
    assert stream.isOpened() is True
    (ret, frame) = stream.read()
    assert ret is True
    test = opt_flow.extract(frame)
    (r, c, _) = frame.shape
    assert test.shape == (r, c, 2)


def _test_optical_flow_get_image(stream, opt_flow):
    # Manually make sure that the returned images look right.
    while stream.isOpened():
        (ret, frame) = stream.read()
        if not ret:
            break
        flow = opt_flow.extract(frame)
        flow_frame = OpticalFlow.get_image(flow)
        cv2.imshow("frame", flow_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    stream.release()
    cv2.destroyAllWindows()

def _test_optical_flow_get_image_from_file():
    directory = './data/1/1/'
    init_image = cv2.imread(directory + '1.jpg')
    opt_flow = OpticalFlow(init_image)
    time_step = 2
    import time
    while True:
        filename = directory + '%s.jpg' % time_step
        image = cv2.imread(filename)
        flow = opt_flow.extract(image)
        flow_image = OpticalFlow.get_image(flow)
        cv2.imshow("frame", flow_image)
        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            break
        cv2.imwrite('flow_%s.png' % time_step, flow_image)
        time_step += 1



def _test_optical_flow_get_features(stream, opt_flow):
    assert stream.isOpened() is True
    (ret, frame) = stream.read()
    assert ret is True
    flow = opt_flow.extract(frame)
    test = OpticalFlow.get_features(flow)
    assert test.shape == (5, 1)


if __name__ == '__main__':
    import pdb
    #_test_optical_flow()
    _test_optical_flow_get_image_from_file()
