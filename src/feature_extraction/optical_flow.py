#!/usr/bin/env python2.7

""" Extracts optical flow features from the drone.
"""

import numpy as np
import cv2


class OpticalFlow(object):
    """ Extracts optical flow features from an image and its predecessor using
        Lucas-Kanade method.
    """
    def __init__(self):
        pass

    def extract(self, img, prev_img):
        pass


def test_optical_flow():
    """ Test optical flow using a sample video.
    """
    sample_video = '../../samples/Cat_Video_1.mp4'

    # Make this code calculate optical flow for only the current and previous
    # frames instead of using a video stream, since we will be getting png
    # images from the drone. Then move it up to the class.
    stream = cv2.VideoCapture(sample_video)
    (ret, init_frame) = stream.read()
    prev_gray = cv2.cvtColor(init_frame, cv2.COLOR_BGR2GRAY)
    hsv = np.zeros_like(init_frame)
    hsv[..., 1] = 255

    while stream.isOpened():
        (ret, frame) = stream.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, 0.5, 1, 3, 15, 3, 5, 1, 0)
            mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            hsv[..., 0] = ang*180/np.pi/2
            hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
            rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            # Combine original frame with flow frame.
            img1 = frame
            img2 = rgb
            (h1, w1, d1) = img1.shape[:3]
            (h2, w2, d2) = img2.shape[:3]
            comb = np.zeros((max(h1, h2), w1+w2, max(d1, d2)), np.uint8)
            comb[:h1, :w1, :d1] = img1
            comb[:h2, w1:w1+w2, :d2] = img2

            cv2.imshow("frame", comb)

            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
            elif k == ord('s'):
                cv2.imwrite('opticalfb.png', frame)
                cv2.imwrite('opticalhsv.png', rgb)
            prev_gray = gray
        else:
            stream.release()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.release()
    cv2.destroyAllWindows()
    pass

if __name__ == '__main__':
    test_optical_flow()
