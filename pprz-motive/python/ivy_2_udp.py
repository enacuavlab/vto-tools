#!/usr/bin/env python3

#socat - UDP-RECV:5558,bind=0.0.0.0,reuseaddr


import socket
import logging
import argparse
import numpy as np
import socket,sys
from threading import Thread
from ivy.std_api import *
from scipy.spatial.transform import Rotation

IVYAPPNAME = 'Ivy_2_udp.py'
IVYBUS = '127:2010'
UDP_IP='127.0.0.1'
UDP_PORT=5558

I2P = 1. / 2**8    # integer to position
#I2V = 1. / 2**19   # integer to velocity
I2W = 1. / 2**12   # integer to angle

class IvyThread:
  def __init__(self,bus):
    self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM )
    self.dict_plane_attitude = {}
    self.dict_plane_estimator = {}
    self.dict_plane_navigation = {}
    logging.getLogger('Ivy').setLevel(logging.ERROR)
    readymsg = '%s READY' % IVYAPPNAME
    IvyInit(IVYAPPNAME,readymsg,0,self.on_cnx,0)
    IvyStart(bus)
    IvyBindMsg(self.on_plane_attitude, '([0-9]+ ATTITUDE .*)')
    IvyBindMsg(self.on_plane_estimator, '([0-9]+ ESTIMATOR .*)')
    IvyBindMsg(self.on_plane_navigation, '([0-9]+ NAVIGATION .*)')
    IvyBindMsg(self.on_rotorcraft_fp, '([0-9]+ ROTORCRAFT_FP .*)')

  def on_cnx(self, dum1, dum2):
    print(dum1,dum2)

  def on_rotorcraft_fp(self, *larg):
    words=(larg[1].split())
    posf = [I2P*float(i) for i in words[2:5]]
    tmp=posf[0];posf[0]=-tmp;tmp=posf[1];posf[1]=-tmp;
    angles = [I2W*np.rad2deg(float(i)) for i in words[8:11]]
    self.build_snd(words[0],posf,Rotation.from_euler('xyz',[-angles[1],-angles[2],angles[0]], degrees=True).as_quat())

  def on_plane_attitude(self, *larg):
    words=(larg[1].split())
    self.dict_plane_attitude[int(words[0])]=words[2:5]
    self.check_plane(int(words[0]))

  def on_plane_estimator(self, *larg):
    words=(larg[1].split())
    self.dict_plane_estimator[int(words[0])]=words[2]
    self.check_plane(int(words[0]))

  def on_plane_navigation(self, *larg):
    words=(larg[1].split())
    self.dict_plane_navigation[int(words[0])]=words[4:6]
    self.check_plane(int(words[0]))

  def check_plane(self, key):
    if ((key in self.dict_plane_attitude) and (key in self.dict_plane_estimator) and (key in self.dict_plane_navigation)):
      posf = [-float(i) for i in self.dict_plane_navigation[key]]
      posf.append(float(self.dict_plane_estimator[key]))
      angles = [np.rad2deg(float(i)) for i in self.dict_plane_attitude[key]]
      self.build_snd(str(key),posf,Rotation.from_euler('xzy',[-angles[2],angles[0],-angles[1]], degrees=True).as_quat())
      self.dict_plane_attitude.pop(key);self.dict_plane_estimator.pop(key);self.dict_plane_navigation.pop(key)

  def build_snd(self,acid,posf,quatf):
    msg="ivy "+acid+" "
    msg+=(" ".join(["%.3f" % nb for nb in posf]))
    msg+=" "+(" ".join(["%.6f" % nb for nb in quatf]))
    data=msg.encode( 'utf-8' )
    data+=b'\n'
    self.sock.sendto(data,(UDP_IP,UDP_PORT))
    print(msg)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  args = parser.parse_args()
  IvyThread(IVYBUS)
  #IvyStop()
