#!/bin/bash

#gst-launch-1.0 -v ximagesrc ! video/x-raw,framerate=20/1 ! videoscale ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=127.0.0.1 port=5000

gst-launch-1.0 -v videotestsrc ! clockoverlay shaded-background=true font-desc="Sans, 36" \
       	! video/x-raw,width=320,height=180,framerate=25/1 \
	! videoscale \
	! videoconvert \
	! x264enc tune=zerolatency bitrate=500 speed-preset=superfast \
	! rtph264pay \
	! udpsink host=127.0.0.1 port=5000 &
sink1_pid=$!

gst-launch-1.0 -v videotestsrc ! clockoverlay shaded-background=true font-desc="Sans, 36" \
       	! video/x-raw,width=320,height=180,framerate=25/1 \
	! videoscale \
	! videoconvert \
	! x264enc tune=zerolatency bitrate=500 speed-preset=superfast \
	! rtph264pay \
	! udpsink host=127.0.0.1 port=5010 &
sink2_pid=$!

gst-launch-1.0 -v videotestsrc ! clockoverlay shaded-background=true font-desc="Sans, 36" \
       	! video/x-raw,width=320,height=180,framerate=25/1 \
	! videoscale \
	! videoconvert \
	! x264enc tune=zerolatency bitrate=500 speed-preset=superfast \
	! rtph264pay \
	! udpsink host=127.0.0.1 port=5020 &
sink3_pid=$!

gst-launch-1.0 -v videotestsrc ! clockoverlay shaded-background=true font-desc="Sans, 36" \
       	! video/x-raw,width=320,height=180,framerate=25/1 \
	! videoscale \
	! videoconvert \
	! x264enc tune=zerolatency bitrate=500 speed-preset=superfast \
	! rtph264pay \
	! udpsink host=127.0.0.1 port=5030 &
sink4_pid=$!

#-------------------------------------------------------------------------------
read -p "Press to stop"
kill $sink1_pid $sink2_pid $sink3_pid $sink4_pid
