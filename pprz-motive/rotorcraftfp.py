#!/usr/bin/env python3

#/home/pprz/Projects/paparazzi/sw/ground_segment/python/natnet3.x/natnet2ivy.py -ac 114 114 -s 192.168.1.230 -f 10 -g

#/home/pprz/Projects/paparazzi/sw/ground_segment/tmtc/link  -d /dev/paparazzi/xbee -transport xbee -s 57600

#stdbuf -oL -eL ivyprobe '(ROTORCRAFT_FP.*)' | ./rotorcraftfp.py

#Link sent  'ROTORCRAFT_FP -890 -1016 5 -5242 0 -5242 -95 -2 1692 0 0 5 1692 0 0'

import sys
import numpy as np
from scipy.spatial.transform import Rotation

I2P = 1. / 2**8    # integer to position
I2V = 1. / 2**19   # integer to velocity
I2W = 1. / 2**12   # integer to angle

while True:
  line=sys.stdin.readline()
  words = line.split() 
  pos_bytes=words[3:6] 
  vel_bytes=words[6:9] 
  eul_bytes=words[9:12] 
  if(len(eul_bytes)==0): continue
  pos=np.zeros(3);vel=np.zeros(3)
  pos[0] = I2P*float(pos_bytes[0]) # north
  pos[1] = I2P*float(pos_bytes[1]) # east
  pos[2] = I2P*float(pos_bytes[2]) # up
  vel[0] = I2V*float(vel_bytes[0]) # vnorth
  vel[1] = I2V*float(vel_bytes[1]) # veast
  vel[2] = I2V*float(vel_bytes[2]) # vup
  phi = np.rad2deg(I2W*float(eul_bytes[0])) 
  theta = np.rad2deg(I2W*float(eul_bytes[1])) 
  psi = np.rad2deg(I2W*float(eul_bytes[2])) 

  print(f'{int(psi):+04}',f'{int(phi):+04}',f'{int(theta):+04}')
