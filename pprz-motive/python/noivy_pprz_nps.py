#!/usr/bin/env python3

#pip install numpy-quaternion

#/home/pprz/Projects/paparazzi/sw/simulator/pprzsim-launch -a Explorer_114 -t nps

#stdbuf -oL -eL ivyprobe '(.NPS_SPEED_POS.*|.NPS_RATE_ATTITUDE.*)' | ./pprz_nps.py  | tee >(socat - udp-sendto:127.0.0.1:5558)

#Explorer_114_NPS sent  ' NPS_RATE_ATTITUDE -0.135402 -0.123302 -0.006576 -0.153438 -0.083385 -0.015105'
#Explorer_114_NPS sent  ' NPS_SPEED_POS -0.012821 -0.022039 0.004053 -0.016564 0.004399 -0.003870 0.054424 0.124756 -3.901687'


import sys,time
import numpy as np
from scipy.spatial.transform import Rotation

posf = np.zeros(3);quatf = np.zeros(4)
while True:
  line=sys.stdin.readline()
  words = line.split()
  msg=(words[3:][:1])
  if(len(msg)==0): continue
  if(msg[0]=="NPS_SPEED_POS"):
    data=(words[4:])
    posf[0]=-float(data[7]);posf[1]=-float(data[6]);posf[2]=-float(data[8][:-1]);
  elif(msg[0]=="NPS_RATE_ATTITUDE"):
    data=(words[4:])
    phi=-float(data[4]);theta=-float(data[5][:-1]);psi=float(data[3])
    rot = Rotation.from_euler('xyz',[phi,theta,psi], degrees=True)
    quatf=rot.as_quat()
  if(np.all(posf==0.)or(np.all(quatf==0.))): continue
  msg="114 "
  msg+=(" ".join(["%.3f" % nb for nb in posf]))
  msg+=" "+(" ".join(["%.6f" % nb for nb in quatf]))
  print(msg,flush=True)
  posf = np.zeros(3);quatf = np.zeros(4)
