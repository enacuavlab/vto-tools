#!/bin/bash

#-------------------------------------------------------------------------------
video_caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96"

YOUTUBE_URL="rtmp://a.rtmp.youtube.com/live2/x"
KEY="rghc-mqk1-ubx3-5501"

gst-launch-1.0 -e compositor name=videomix \
  sink_0::xpos=0     sink_0::ypos=0  sink_0::alpha=0 \
  sink_1::xpos=0     sink_1::ypos=0 \
  sink_2::xpos=320   sink_2::ypos=0 \
  sink_3::xpos=0     sink_3::ypos=180 \
  sink_4::xpos=320   sink_4::ypos=180 \
  videotestsrc pattern=1 is-live=1 \
      ! video/x-raw, width=640, height=360 \
      ! videomix.sink_0 \
  udpsrc caps="application/x-rtp" port=5000 \
      ! rtph264depay ! decodebin \
      ! videoconvert ! videoscale \
      ! video/x-raw,width=320,height=180 \
      ! videomix.sink_1 \
  udpsrc caps="application/x-rtp" port=5010 \
      ! rtph264depay ! decodebin \
      ! videoconvert ! videoscale \
      ! video/x-raw,width=320,height=180 \
      ! videomix.sink_2 \
  udpsrc caps="application/x-rtp" port=5020 \
      ! rtph264depay ! decodebin \
      ! videoconvert ! videoscale \
      ! video/x-raw,width=320,height=180 \
      ! videomix.sink_3 \
  udpsrc caps="application/x-rtp" port=5030 \
      ! rtph264depay ! decodebin \
      ! videoconvert ! videoscale \
      ! video/x-raw,width=320,height=180 \
      ! videomix.sink_4 \
  videomix. \
      ! x264enc bitrate=2000 byte-stream=false key-int-max=60 bframes=0 aud=true tune=zerolatency \
      ! "video/x-h264,profile=main" \
      ! flvmux streamable=true name=mux \
      ! rtmpsink location="$YOUTUBE_URL/$KEY" \
   audiotestsrc \
      ! voaacenc bitrate=128000 \
      ! mux. &

#-------------------------------------------------------------------------------
read_pid=$!
read -p "Press to stop"
kill $read_pid
