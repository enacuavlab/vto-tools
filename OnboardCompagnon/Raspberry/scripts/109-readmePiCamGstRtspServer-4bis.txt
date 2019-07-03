gst-launch-1.0 rpicamsrc bitrate=1000000 vflip=true ! video/x-h264,width=640,height=480,framerate=15/1 ! h264parse config-interval=1 ! tee name=streams ! queue ! shmsink socket-path=/tmp/camera1 wait-for-connection=false sync=false streams. ! queue ! omxh264dec ! shmsink socket-path=/tmp/camera2 wait-for-connection=false sync=false

~/gst-rtsp-server-1.10.4/examples/test-launch "( shmsrc socket-path=/tmp/camera1 do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay config-interval=1 name=pay0 pt=96 )"

gst-launch-1.0 rtspsrc location=rtsp://192.168.43.74:8554/test ! rtph264depay ! avdec_h264 ! xvimagesink sync=false



#!/usr/bin/python3

import numpy as np
import threading
import cv2
import time



faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

acquisition_cpt = 0
processing_cpt = 0
frame = None


def open_cam():
  return cv2.VideoCapture('shmsrc socket-path=/tmp/camera2 ! '
    'video/x-raw,width=640,height=480,framerate=15/1,format=RGB ! '
    'videoconvert ! '
    'appsink sync=false',cv2.CAP_GSTREAMER)


def open_output():
  return cv2.VideoWriter('appsrc ! queue ! ' 
    'shmsink socket-path=/tmp/camera3 '
    'wait-for-connection=false async=false sync=false ',
    0, 15.0, (640,480))


def data_acquisition(cap,out,condition):
  global acquisition_cpt,frame
  print("data_acquisition thread")
  while True:
    grabbed,frame = cap.read()
    if grabbed:
      with condition:
        acquisition_cpt = acquisition_cpt + 1
#        print("acquisition_cpt ",acquisition_cpt)
        condition.notify()


def data_processing(cap,out,condition):
  global processing_cpt
  print("data_processing thread")
  while True:

    with condition:
      condition.wait()
      img = frame.copy()

    processing_cpt = processing_cpt + 1
    print("processing_cpt ",processing_cpt)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
      gray,
      scaleFactor=1.3,
      minNeighbors=5,
      minSize=(30, 30)
    )

    for (x,y,w,h) in faces:
      print('x=',x," y=",y," w=",w," h=",h)

#    for (x,y,w,h) in faces:
#      cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
#      roi_gray = gray[y:y+h, x:x+w]
#      roi_color = img[y:y+h, x:x+w]

#    out.write(img)


if __name__ == '__main__':

  cap = open_cam()
  out = open_output()
  time.sleep(0.1)
 
  if not cap.isOpened() or not out.isOpened():
    print("not opened")
    quit()

  threads = []
  condition = threading.Condition()
  for func in [data_acquisition, data_processing]:
    threads.append(threading.Thread(target=func, args=(cap,out,condition)))
    threads[-1].start() 
  for thread in threads:
    thread.join()

  cap.release()
