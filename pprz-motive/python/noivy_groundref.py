#!/usr/bin/env python3

# OPTITRACK_MOTIVE : Z UP

#/home/pprz/Projects/paparazzi/sw/ground_segment/python/natnet3.x/natnet2ivy.py -ac 114 114 -s 192.168.1.230 -f 10 -g

#stdbuf -oL -eL ivyprobe '(ground GROUND_REF.*)' | ./groundref.py

#natnet2ivy sent  'ground GROUND_REF 114 LTP_ENU -2.533431053161621,-2.5710501670837402,0.04404295235872269 0.006752014160254505,-0.008111000061153187,0.006487146020030009 0.9994727969169617,0.013409178704023361,-0.004338078200817108,-0.029251547530293465 0.0,0.0,0.0 29319.955555555556'

import sys,time
import numpy as np
from scipy.spatial.transform import Rotation

while True:
  line=sys.stdin.readline()
  words = line.split()
  pos=(words[6:][:1])
  speed=(words[6:][1:2])
  quat=(words[6:][2:3])
  if(len(pos)==0): continue
  tmp = np.array([float(x) for x in pos[0].split(',')])
  posf = tmp.copy(); posf[0] = tmp[1]; posf[1] = tmp[0]
  tmp = np.array([float(x) for x in speed[0].split(',')])
  speedf = tmp.copy(); speedf[0] = tmp[1]; speedf[1] = tmp[0]
  quatf = np.array([float(x) for x in quat[0].split(',')])
  # natnet2ivy switched quaternions (quat[3],quat[0],quat[1],quat[2]) from natnet convention qw,qx,qy,qz
  # scipy convention is qx,qy,qz,qw
  rot = Rotation.from_quat(quatf) 
  # rotation order X(pitch),Y(yaw),Z(roll)
  rot_euler = rot.as_euler('xyz', degrees=True)
  
  psi = rot_euler[0]-180 if rot_euler[0] > 0 else 180+rot_euler[0] # YAW [0..179,-179..0]  Z DOWN
  phi = -1*rot_euler[1] # ROLL 
  theta = rot_euler[2]  # PITCH

  print(f'{int(psi):+04}',f'{int(phi):+04}',f'{int(theta):+04}')
