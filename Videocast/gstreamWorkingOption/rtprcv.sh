#!/bin/bash

gst-launch-1.0 -v udpsrc port=5050 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! autovideosink &

pid=$!

read -p "Press to stop"
kill $pid
