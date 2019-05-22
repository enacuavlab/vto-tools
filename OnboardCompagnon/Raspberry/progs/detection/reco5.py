#!/usr/bin/python3

from imutils.video import VideoStream
import socket
import time

udpsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
vs = VideoStream(usePiCamera=True, resolution=(640, 480)).start()
#vs = VideoStream(0).start() For USB camera

time.sleep(2)

while True:
  udpsock.sendto(vs.read(), ('192.168.43.181',5000))

udpsock.close()
vs.stop()
