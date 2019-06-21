
MULTITHREAD : Capture + Image Process + Broadcast 

----------------------------------------------------------------------

#!/usr/bin/python3
 
import threading
import cv2
import time

# 0)
#gst-inspect-1.0 rpicamsrc

# 1)
#~/gst-rtsp-server-1.10.4/examples/test-launch "( shmsrc socket-path=/tmp/video-sock do-timestamp=true ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay config-interval=1 name=pay0 pt=96 )"

# 2)
#GST_DEBUG=3 gst-launch-1.0 -v rpicamsrc ! video/x-h264,width=640,height=480,framerate=15/1 ! h264parse config-interval=1 ! tee name=streams ! queue ! shmsink socket-path=/tmp/video-sock shm-size=10000000 wait-for-connection=0 async=false sync=false streams. ! queue ! omxh264dec ! videoconvert ! fakesink async=false sync=false

# 3)
#gst-launch-1.0 rtspsrc location=rtsp://192.168.43.73:8554/test ! rtph264depay ! avdec_h264 !  xvimagesink sync=false

framecount = 0

class ImageGrabber():
  def __init__(self, pipe):
    self.cap = cv2.VideoCapture(pipe,cv2.CAP_GSTREAMER)
    self.grabbed, self.frame = self.cap.read()
    self.read_lock = threading.Lock()

  def start(self):
    self.thread = threading.Thread(target=self.update, args=())
    self.thread.start()

  def update(self):
    global framecount
    while True:
      grabbed, frame = self.cap.read()
      with self.read_lock:
        self.grabbed = grabbed
        self.frame = frame
        framecount = framecount + 1
        print("framecount ",framecount)

  def read(self):
    with self.read_lock:
      frame = self.frame.copy()
      grabbed = self.grabbed
    return grabbed, frame  


if __name__ == '__main__':

  grabber = ImageGrabber('rpicamsrc ! '
    'video/x-h264,width=640,height=480,framerate=15/1 ! '
    'h264parse config-interval=1 ! '
    'tee name=streams ! '
    'queue ! '
    'shmsink socket-path=/tmp/video-sock '
    'wait-for-connection=0 async=false sync=false '
    'streams. ! queue ! omxh264dec ! '
    'videoconvert ! '
    'appsink')

#    'shm-size=10000000 wait-for-connection=0 async=false sync=false '
  time.sleep(0.1)
  if not grabber.cap.isOpened():
    print("not opened")
    quit()

  grabber.start()

  imagecount = 0
  while True:
    grabbed, frame = grabber.read()
    print("imagecount ",imagecount)
    imagecount = imagecount + 1
    time.sleep(3)

#  cam.release()
