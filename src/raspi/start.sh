#!/bin/bash

direct='/tmp/stream'
if [ ! -d "$direct" ]; then
    mkdir /tmp/stream
    echo "Creating directory /tmp/stream/"
fi

echo "Getting png stream"
raspistill --nopreview -w 640 -h 480 -q 5 -o /tmp/stream/pic.jpg -tl 1000 -t 9999999 -th 0:0:0 &

cd ~
cd '/home/pi/mjpg-streamer-code-182/mjpg-streamer'
LD_LIBRARY_PATH=./ ./mjpg_streamer -i "./input_file.so -f /tmp/stream -n pic.jpg" -o "./output_http.so -w ./www"
