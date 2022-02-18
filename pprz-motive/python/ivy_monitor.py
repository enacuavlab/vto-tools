#!/usr/bin/env python3

#/home/pprz/Projects/paparazzi/sw/ground_segment/python/natnet3.x/natnet2ivy.py -ac 114 114 -s 192.168.1.230 -f 120 -g

#stdbuf -oL -eL ivyprobe '(ground GROUND_REF.*)' | ./monitor.py -f 120 -t 50

import time,sys,argparse
import tkinter as tk
import numpy as np
from scipy.spatial.transform import Rotation
from threading import Timer, Thread, Event


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

  def update_lab1(self,string):
    try:
      self.lab1['text'] = string
    except RuntimeError:
      exit()

  def update_lab2(self,string):
    try:
      self.lab2['text'] = string
    except RuntimeError:
      exit()


class Compute1(Thread):
  def __init__(self,g,i):
    Thread.__init__(self)
    self.g = g
    self.i = i

  def run(self):
    while self.i.available_string.wait():
      data = self.i.string
      self.i.available_string.clear()
      pos = (np.fromiter(data[:1][0].split(','),dtype=float))
      spd = (np.fromiter(data[1:2][0].split(','),dtype=float))
      rot = Rotation.from_quat(np.fromiter(data[2:3][0].split(','),dtype=float))
      rot_euler = rot.as_euler('xyz', degrees=True)
      psi = rot_euler[0]-180 if rot_euler[0] > 0 else 180+rot_euler[0] # YAW
      phi = -1*rot_euler[1] # ROLL 
      theta = rot_euler[2]  # PITCH
      tmp = (f'{int(psi):+04}',f'{int(phi):+04}',f'{int(theta):+04}')
      g.update_lab1(tmp)


class Compute2(Thread):
  def __init__(self,g,i):
    Thread.__init__(self)
    self.g = g
    self.i = i

  def run(self):
    while self.i.available_outcpt.wait():
      data = self.i.outcpt
      self.i.available_outcpt.clear()
      g.update_lab2(data)


class Input(Thread):
  def __init__(self, t, tole):
    Thread.__init__(self)
    self.t = t
    self.tole = tole
    self.string = ''
    self.stamp = 0.
    self.outcpt = 0
    self.available_string = Event()
    self.available_outcpt = Event()

  def run(self):
    cpt=0
    while True:
      line=sys.stdin.readline()
      words = line.split()
      if(len(words[6:][2:3])==0): continue
      if(cpt==0):cpt=1;self.t.start()
      tmp = time.time()
      if int(self.stamp)!= 0: 
        delay = tmp - self.stamp 
        if (delay>=self.tole):
          self.outcpt=self.outcpt+1
          self.available_outcpt.set()
      self.stamp = tmp
      self.string = words[6:]
      self.available_string.set()

  def tick(self):
    delay=time.time()-self.stamp
    if (delay>=self.tole):
      self.outcpt=self.outcpt+1
      self.available_outcpt.set()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-f', '--freq', dest='freq', default=120, type=int, help="transmit frequency")
  parser.add_argument('-t', '--tole', dest='tole', default=50, type=int, help="percent tolerance")
  args = parser.parse_args()

  def tickcb():
    i.tick()

  g = Gui()
  t = Timer(1/args.freq,tickcb)
  i = Input(t,(1.0/args.freq)*(100.+args.tole)/100.)
  c1 = Compute1(g,i)
  c2 = Compute2(g,i)
  c1.start()
  c2.start()
  i.start()
  g.mainloop()
  i.join()
  c1.join()
  c2.join()
