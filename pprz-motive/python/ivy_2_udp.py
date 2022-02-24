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

#    IvyBindMsg(self.on_navigation, '([0-9]* NAVIGATION.*)')
#   IvyBindMsg(self.on_nps_speed_pos, '([0-9]* NPS_SPEED_POS.*)')
#   IvyBindMsg(self.on_nps_rate_attitude, '([0-9]* NPS_RATE_ATTITUDE.*)')

#  def on_nps_speed_pos(self, *larg):
#    words=(larg[1].split())
#    self.dict_pos[int(words[0])]=words[8:11]
#    self.checksnd(int(words[0]))
#
#  def on_nps_rate_attitude(self, *larg):
#    words=(larg[1].split())
#    self.dict_att[int(words[0])]=words[5:8]
#    self.checksnd(int(words[0]))
#
#  def checksnd(self, key):
#    posf = np.zeros(3);quatf = np.zeros(4)
#    if ((key in self.dict_pos) and (key in self.dict_att)):
#      posf[0]=-float(self.dict_pos[key][1])
#      posf[1]=-float(self.dict_pos[key][0])
#      posf[2]=-float(self.dict_pos[key][2])
#      psi=float(self.dict_att[key][0])
#      phi=-float(self.dict_att[key][1])
#      theta=-float(self.dict_att[key][2])
#      rot = Rotation.from_euler('xyz',[phi,theta,psi], degrees=True)
#      quatf=rot.as_quat()
#      msg="ivy "+str(key)+" "
#      msg+=(" ".join(["%.3f" % nb for nb in posf]))
#      msg+=" "+(" ".join(["%.6f" % nb for nb in quatf]))
#      self.dict_pos.pop(key)
#      self.dict_att.pop(key)
#      data=msg.encode( 'utf-8' )
#      data+=b'\n'
#      self.sock.sendto(data,(UDP_IP,UDP_PORT))
#      print(msg)
#
#  def on_nps_motion(self, *larg):
#    posf = np.zeros(3);quatf = np.zeros(4)
#    words=(larg[1].split())
#    posf[0]=-float(words[3])
#    posf[1]=-float(words[2])
#    posf[2]=-float(words[4])
#    psi=float(words[5])
#    phi=-float(words[6])
#    theta=-float(words[7])
#    rot = Rotation.from_euler('xyz',[phi,theta,psi], degrees=True)
#    quatf=rot.as_quat()
#    msg="ivy "+words[0]+" "
#    msg+=(" ".join(["%.3f" % nb for nb in posf]))
#    msg+=" "+(" ".join(["%.6f" % nb for nb in quatf]))
#    data=msg.encode( 'utf-8' )
#    data+=b'\n'
#    self.sock.sendto(data,(UDP_IP,UDP_PORT))
#    print(msg)

  def on_cnx(self, dum1, dum2):
    print(dum1,dum2)

  def on_rotorcraft_fp(self, *larg):
    posf = np.zeros(3);quatf = np.zeros(4)
    words=(larg[1].split())
    posf = [I2P*float(i) for i in words[2:5]]
    quatf = [I2W*np.rad2deg(float(i)) for i in words[8:11]]
    print(words[8:11])
    print(quatf)

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
      self.build_snd(key,posf,Rotation.from_euler('xzy',[-angles[2],angles[0],-angles[1]], degrees=True).as_quat())
      self.dict_plane_attitude.pop(key);self.dict_plane_estimator.pop(key);self.dict_plane_navigation.pop(key)

  def build_snd(self,acid,posf,quatf):
    msg="ivy "+str(acid)+" "
    msg+=(" ".join(["%.3f" % nb for nb in posf]))
    msg+=" "+(" ".join(["%.6f" % nb for nb in quatf]))
    data=msg.encode( 'utf-8' )
    data+=b'\n'
#    self.sock.sendto(data,(UDP_IP,UDP_PORT))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  args = parser.parse_args()
  IvyThread(IVYBUS)
  #IvyStop()
