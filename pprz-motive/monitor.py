#!/usr/bin/env python3

#/home/pprz/Projects/paparazzi/sw/ground_segment/python/natnet3.x/natnet2ivy.py -ac 114 114 -s 192.168.1.230 -f 10 -g

#stdbuf -oL -eL ivyprobe '(ground GROUND_REF.*)' | ./monitor.py -f 10

import time,sys,argparse
import tkinter as tk
import numpy as np
from scipy.spatial.transform import Rotation
from threading import Timer, Thread


class Timer(Timer):
  def run(self):
    while not self.finished.is_set():
      self.finished.wait(self.interval)
      self.function(*self.args, **self.kwargs)

    self.finished.set()


class Gui(tk.Tk):
  def __init__(self):
    super(Gui, self).__init__()
    self.lab1 = tk.Label(self, text="XXXXXXXXXXXXX")
    self.lab2 = tk.Label(self, text="XXXXXXXXXXXXX")
    self.lab1.pack()
    self.lab2.pack()

  def close():
    self.destroy()

  def tick(self,i):
    try:
      self.lab1['text'] = i.string1
      self.lab2['text'] = i.string2
    except RuntimeError:
      exit()


class Input(Thread):
  def __init__(self, t):
    Thread.__init__(self)
    self.t = t
    self.string1 = ''
    self.string2 = ''
    self.stamp = 0.
    self.cpt = 0

  def run(self):
    cpt=0
    while True:
      line=sys.stdin.readline()
      words = line.split()
      pos=(words[6:][:1])
      speed=(words[6:][1:2])
      quat=(words[6:][2:3])
      if(len(quat)==0): continue
      if(cpt==0):cpt=1;self.t.start()
      self.stamp = time.time()
      self.procline(pos,speed,quat)

  def procline(self, pos,speed,quat):
    tmp = np.array([float(x) for x in pos[0].split(',')])
    posf = tmp.copy(); posf[0] = tmp[1]; posf[1] = tmp[0]
    tmp = np.array([float(x) for x in speed[0].split(',')])
    speedf = tmp.copy(); speedf[0] = tmp[1]; speedf[1] = tmp[0]
    quatf = np.array([float(x) for x in quat[0].split(',')])
    rot = Rotation.from_quat(quatf)
    rot_euler = rot.as_euler('xyz', degrees=True)
    psi = rot_euler[0]-180 if rot_euler[0] > 0 else 180+rot_euler[0] # YAW
    phi = -1*rot_euler[1] # ROLL 
    theta = rot_euler[2]  # PITCH
    self.string1 = (f'{int(psi):+04}',f'{int(phi):+04}',f'{int(theta):+04}')

  def tick(self):
    delta = (time.time()-self.stamp)
    if delta > 1: self.cpt = self.cpt+1
    self.string2 = str(self.cpt)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-f', '--freq', dest='freq', default=10, type=int, help="transmit frequency")
  args = parser.parse_args()

  def tickcb():
    i.tick()
    g.tick(i)
    i.string1 = "XXXXXXXXXXXXX"

  g = Gui()
  t = Timer(1/args.freq,tickcb)
  i = Input(t)
  i.start()
  g.mainloop()
  i.join()
