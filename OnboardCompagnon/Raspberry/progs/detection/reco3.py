#!/usr/bin/python3

#--------------------------------------------------------------------------------------------- 
from imutils.video import VideoStream
import time
import cv2
import sys 

#cap = cv2.VideoCapture(0)
vs = VideoStream(usePiCamera=True, resolution=(640, 480)).start()
#vs = VideoStream(0).start() For USB camera

#Popen(r'c:\gstreamer\1.0\x86_64\bin\gst-launch-1.0 udpsrc port={} ...

time.sleep(2.0)

while True:

  grabbed, frame = vs.read() 

  #ret, frame = cap.read()

  #frame = vs.read()
  sys.stdout.buffer.write(frame)
  sys.stdout.flush()

vs.stop()
