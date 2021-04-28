#!/usr/bin/python3

'''

gst-launch-1.0 udpsrc port=5700 ! application/x-rtp, encoding-name=H264,payload=96 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false

gst-launch-1.0 udpsrc port=5700 ! application/x-rtp ! rtph264depay ! h264parse ! matroskamux ! filesink location="test.mkv"

nc -ul 4200

'''
import socket
import numpy as np
import cv2
from cv2 import aruco
import picamera
import picamera.array
import shlex, subprocess
from fractions import Fraction
from time import sleep

resolution0=(1280,720)
framerate0=25
ip0="127.0.0.1"
ip1="127.0.0.1"
port1=5600
port2=5700
port3=4200
bitrate1=500000
bitrate2=500000
calib_file = '/home/pi/Projects/opencv_test/test.xml'

camera = picamera.PiCamera(resolution=resolution0)

#------------------------------------------------------------------------------
motion_dtype = np.dtype([
  ('x', 'i1'),
  ('y', 'i1'),
  ('sad', 'u2'),
  ])

class MyMotionDetector(object):
  def __init__(self, camera):
    width, height = camera.resolution
    self.cols = (width + 15) // 16
    self.cols += 1 # there's always an extra column
    self.rows = (height + 15) // 16

  def write(self, s):
    data = np.frombuffer(s, dtype=motion_dtype)
    data = data.reshape((self.rows, self.cols))
    data = np.sqrt(np.square(data['x'].astype(np.float))+np.square(data['y'].astype(np.float))).clip(0, 255).astype(np.uint8)
    if (data > 60).sum() > 10: print('Motion detected!')
    return len(s)


#------------------------------------------------------------------------------
class MyAnalysis(picamera.array.PiRGBAnalysis):
  def __init__(self, camera):
    super(MyAnalysis, self).__init__(camera)
    cmd='appsrc ! v4l2convert ! v4l2h264enc extra-controls="controls,video_bitrate=%d" output-io-mode=dmabuf-import \
            ! rtph264pay pt=96 config-interval=1 ! udpsink host=%s port=%d' % (bitrate2,ip0,port2)
    self.strOut =  cv2.VideoWriter(cmd,cv2.CAP_GSTREAMER, float(camera.framerate), camera.resolution)
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    camera.exposure_mode = 'sports'     
    self.aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    self.parameters =  aruco.DetectorParameters_create()
    self.markerlength=0.07
    f = cv2.FileStorage(calib_file,cv2.FILE_STORAGE_READ)
    self.cameraMatrix = f.getNode("matrix").mat()
    self.distCoeffs = f.getNode("dist").mat()
    self.notfound = 0

  def analyse(self, array):
    gray3 = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    markerCorners,markersIds,rejectedImgPoints = aruco.detectMarkers(gray3, self.aruco_dict, parameters=self.parameters)
    if markersIds == None:
      gray1 = cv2.cvtColor(gray3, cv2.COLOR_GRAY2BGR)
#      if(self.notfound<10):self.notfound=self.notfound+1
#      else:
#        self.notfound=0
#        if camera.exposure_mode == 'sports': camera.exposure_mode = 'spotlight' # or camera.shutter_speed=198 => camera.exposure_speed
#        else:camera.exposure_mode = 'sports'
    else:
      self.notfound=0
      gray3b = aruco.drawDetectedMarkers(gray3,markerCorners,markersIds)
      rvecs, tvecs, markerPoints = aruco.estimatePoseSingleMarkers(markerCorners,self.markerlength,self.cameraMatrix,self.distCoeffs)
      #aruco.drawAxis(gray3, self.cameraMatrix,self.distCoeffs, rvec, tvec, 0.01) 
      #inverted signed with cpp version
      msgbuff='%d %d %d\n' % ((int)(-1000*tvecs[0][0][0]),(int)(-1000*tvecs[0][0][1]),(int)(1000*tvecs[0][0][2]))
      self.sock.sendto(msgbuff.encode(), (ip1, port3))
      gray1 = cv2.cvtColor(gray3b, cv2.COLOR_GRAY2BGR)
    self.strOut.write(gray1)


#------------------------------------------------------------------------------
if __name__ == '__main__':

  cmd="gst-launch-1.0 fdsrc ! h264parse ! rtph264pay pt=96 config-interval=1 ! udpsink host=%s port=%d" % (ip0,port1)
  gstreamer = subprocess.Popen(shlex.split(cmd),stdin=subprocess.PIPE)

  camera.start_recording(gstreamer.stdin, format='h264', bitrate=bitrate1, splitter_port=0)
  camera.start_recording('test.h264', format='h264', splitter_port=1)
  camera.start_recording(MyAnalysis(camera), format='rgb', splitter_port=2)

# cannot be run with changing exposure mode
# camera.start_recording('/dev/null', format='h264',motion_output=MyMotionDetector(camera),splitter_port=3)

  try:
    while True:
      sleep(0.5)
  except KeyboardInterrupt:
    camera.stop_recording()
    gstreamer.terminate()
    exit()
