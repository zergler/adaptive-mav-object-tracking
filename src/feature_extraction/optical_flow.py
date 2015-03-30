#!/usr/bin/env python2.7

""" Extracts optical flow features from the drone.
"""

import numpy as np
import cv2


class OpticalFlow(object):
    """ Extracts optical flow features from an image and its predecessor using
        Lucas-Kanade method.
    """
    def __init__(self, test_frame):
        # Parameters of the camera/images.
        self.prev_gray = cv2.cvtColor(test_frame, cv2.COLOR_BGR2GRAY)
        self.hsv = np.zeros_like(test_frame)
        self.hsv[..., 1] = 255

        # Parameters for farneback optical flow.
        self.pyr_scale = 0.5   # next layer is twice smaller than the previous
        self.levels = 5        # number of pyramid layers including the initial image
        self.winsize = 13      # averaging window size
        self.iterations = 10   # number of iterations at each pyramid level
        self.poly_n = 5        # size of the pixel neighborhood used to find polynomial expansion in each pixel
        self.poly_sigma = 1.1  # standard deviation of the Gaussian used to smooth derivatives used as a basis for the polynomial expansion
        self.flags = 0         # no flags (OPTFLOW_USE_INITIAL_FLOW, OPTFLOW_FARNEBACK_GAUSSIAN)

    def extract(self, frame):
        """ Extract optical flow from the current frame.
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

        # Convert the flow to polar and normalize.
        (mag, ang) = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        self.hsv[..., 0] = ang*180/np.pi/2
        self.hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        flow_frame = cv2.cvtColor(self.hsv, cv2.COLOR_HSV2BGR)
        self.prev_gray = cur_gray
        return flow_frame


def test_optical_flow(test_filename):
    """ Test optical flow using a sample video.
    """
    # Get the video used for the test.
    stream = cv2.VideoCapture(test_filename)
    (ret, test_frame) = stream.read()

    opt_flow = OpticalFlow(test_frame)
    while stream.isOpened():
        (ret, frame) = stream.read()
        if ret:
            opt_frame = opt_flow.extract(frame)
            cv2.imshow("frame", opt_frame)
        else:
            stream.release()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.release()
    cv2.destroyAllWindows()
    pass


def main():
    test_filename = '../../samples/Cat_Video_1.mp4'
    test_optical_flow(test_filename)

if __name__ == '__main__':
    main()
