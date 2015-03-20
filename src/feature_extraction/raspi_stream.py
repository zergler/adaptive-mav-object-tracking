#!/usr/bin/env python2.7

import cv2
import urllib
import numpy as np
import png
import pdb
import StringIO
import sys
from PIL import Image


# This works (tested) with raspberry pi and camera module but it should work with parrot too.
def main():
    while True:
        try:
            image = url_to_image('http://192.168.1.2:8080')
            cv2.imshow('opencv image server raspi test', image)
            k = cv2.waitKey(0)
            if k == 27:         # wait for ESC key to exit
                cv2.destroyAllWindows()
            elif k == ord('s'):  # wait for 's' key to save and exit
                cv2.imwrite('messigray.png', image)
                cv2.destroyAllWindows()
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            sys.exit(0)


# METHOD #1: OpenCV, NumPy, and urllib
def url_to_image(url):
        # download the image, convert it to a NumPy array, and then read
        # it into OpenCV format
        resp = urllib.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image


def get_stream_raspi():
    # Code credit: Petr Kout'
    # http://petrkout.com/electronics/low-latency-0-4-s-video-streaming-from-raspberry-pi-mjpeg-streamer-opencv/

    stream = urllib.urlopen('http://192.168.1.2:8080')
    r.read()
    ss = ''
    while True:
        ss += stream.read(1024)
        a = ss.find('\xff\xd8')
        b = ss.find('\xff\xd9')
        if a != -1 and b != -1:
            jpg = ss[a:b + 2]
            ss = ss[b + 2:]
            i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
            cv2.imshow('opencv image server raspi test', i)
            if cv2.waitKey(1) == 27:
                exit(0)

if __name__ == '__main__':
    main()
