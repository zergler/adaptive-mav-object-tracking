#!/usr/bin/env python2

import cv2

cap = cv2.VideoCapture('Cat_Video_1.mp4')

while cap.isOpened():
    # Capture frame-by-frame.
    (ret, frame) = cap.read()

    if ret:
        # Our operations on the frame come here.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame.
        cv2.imshow('frame', gray)
    else:
        # When everything is done, release the capture.
        cap.release()

    # Quit using 'q' key.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
