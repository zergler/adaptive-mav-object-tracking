import cv2
import urllib
import numpy as np

# Code credit: Petr Kout'
# http://petrkout.com/electronics/low-latency-0-4-s-video-streaming-from-raspberry-pi-mjpeg-streamer-opencv/

# This works (tested) with raspberry pi and camera module but it should work with parrot too.

stream = urllib.urlopen('http://10.0.0.17:9000/?action=stream')
ss = ''
while True:
    ss += stream.read(1024)
    a = ss.find('\xff\xd8')
    b = ss.find('\xff\xd9')
    if a != -1 and b != -1:
        jpg = ss[a:b + 2]
        ss = ss[b + 2:]
        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
        cv2.imshow('i', i)
        if cv2.waitKey(1) == 27:
            exit(0)
