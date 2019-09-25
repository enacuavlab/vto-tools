#!/bin/bash


gst-launch-1.0 compositor name=videomix \
  sink_0::xpos=0   sink_0::ypos=0 sink_0::alpha=0 \
  sink_1::xpos=0   sink_1::ypos=0 \
  sink_2::xpos=320 sink_2::ypos=0 \
  ! videoconvert \
  ! ximagesink \
  videotestsrc pattern=1 is-live=1 \
  ! video/x-raw, width=640, height=180 \
  ! videomix.sink_0 \
  videotestsrc pattern=smpte timestamp-offset=3000000000 \
  ! "video/x-raw,format=AYUV,width=320,height=180,framerate=(fraction)30/1" \
  ! videomix.sink_1 \
  videotestsrc pattern=smpte \
  ! "video/x-raw,format=AYUV,width=320,height=180,framerate=(fraction)10/1" \
  ! videomix.sink_2
