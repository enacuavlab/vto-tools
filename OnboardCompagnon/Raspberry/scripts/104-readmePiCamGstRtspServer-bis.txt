#!/usr/bin/python3

import cv2
import numpy as np
import time


# 0)
#gst-inspect-1.0 rpicamsrc

# 1)
#~/gst-rtsp-server-1.10.4/examples/test-launch "( shmsrc socket-path=/tmp/video-sock do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay config-interval=1 name=pay0 pt=96 )"

# 2)
#GST_DEBUG=3 gst-launch-1.0 -v rpicamsrc ! video/x-h264,width=640,height=480,framerate=15/1 ! h264parse config-interval=1 ! tee name=streams ! queue ! shmsink socket-path=/tmp/video-sock shm-size=10000000 wait-for-connection=0 async=false sync=false streams. ! queue ! omxh264dec ! videoconvert ! fakesink async=false sync=false

# 3)
#gst-launch-1.0 rtspsrc location=rtsp://192.168.43.73:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false


def makecam():
  return cv2.VideoCapture('rpicamsrc ! '
    'video/x-h264,width=640,height=480,framerate=15/1 ! '
    'h264parse config-interval=1 ! '
    'tee name=streams ! '
    'queue ! '
    'shmsink socket-path=/tmp/video-sock '
    'shm-size=10000000 wait-for-connection=0 async=false sync=false '
    'streams. ! queue ! omxh264dec ! '
    'videoconvert ! '
    'appsink',cv2.CAP_GSTREAMER)


if __name__ == '__main__':

  cam = makecam()
  time.sleep(0.1)
  
  if not cam.isOpened():
    print("not opened")
    quit()

  framecount=0
  while True:
    ret,frame = cam.read()
    if ret==True:
      print("frame ",framecount)
      framecount = framecount + 1

  cam.release()
