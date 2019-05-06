#!/bin/bash

#gst-launch-1.0 ximagesrc startx=1280 use-damage=0 \
gst-launch-1.0 ximagesrc startx=0 endx=321 starty=0 endy=180 use-damage=0 \
! video/x-raw,framerate=25/1 \
! videoscale method=0 \
! videoconvert \
! x264enc tune=zerolatency bitrate=500 speed-preset=superfast \
! rtph264pay config-interval=1 \
! udpsink host=127.0.0.1 port=5000 &
sink_pid=$!
#-------------------------------------------------------------------------------
read -p "Press to stop"
kill $sink_pid
