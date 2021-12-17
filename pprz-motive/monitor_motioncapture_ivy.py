#!/usr/bin/env python3

#/home/pprz/Projects/paparazzi/sw/ground_segment/python/natnet3.x/natnet2ivy.py -ac 116 116 -s 192.168.1.230 -f 10 -g

import logging,time,argparse
import tkinter as tk
import numpy as np
from threading import Timer, Thread, Event
from scipy.spatial.transform import Rotation
from ivy.std_api import *

IVYAPPNAME = 'MonitorMotioncaptureIvy.py'
IVYBUS = '127:2010'

class Gui(tk.Tk):
  def __init__(self,parent):
    tk.Tk.__init__(self,parent)
    self.parent = parent
    self._thread, self._stop = None, True
    self.lab1 = tk.Label(self, text="XXXXXXXXXXXXX")
    self.lab2 = tk.Label(self, text="XXXXXXXXXXXXX")
    self.lab1.pack()
    self.lab2.pack()
    self.minsize(width=180,height=50)
    self.resizable(True,False)
    self.title(IVYAPPNAME)
    self.protocol("WM_DELETE_WINDOW", self.on_close)

  def run(self):
    i=self.scale.get()

  def on_close(self):
    if(self._thread==None) and (self._stop): self.destroy()
    self._thread, self._stop = None, True

  def update_lab1(self,string):
    try: self.lab1['text'] = string
    except RuntimeError: exit()

  def update_lab2(self,string):
    try: self.lab2['text'] = string
    except RuntimeError: exit()


class RepeatTimer(Timer):
  def run(self):
    while not self.finished.wait(self.interval):
      self.function(*self.args, **self.kwargs)

mytimer = None
class IvyThread:
  def __init__(self,bus,freq,tole):
    self.freq=freq
    self.tole=(1.0/freq)*(100.+tole)/100.
    self.cpt=0
    self.stamp=0.
    self.string=''
    self.outcpt=0
    self.available_string = Event()
    self.available_outcpt = Event()
    logging.getLogger('Ivy').setLevel(logging.ERROR)
    readymsg = '%s READY' % IVYAPPNAME
    IvyInit(IVYAPPNAME,readymsg,0,self.on_cnx,0)
    IvyStart(bus)
    IvyBindMsg(self.on_msg_ground_ref_ltp_enu, '(.*LTP_ENU.*)')

  def on_cnx(self, dum1, dum2):
    print(dum1,dum2)

  def on_msg_ground_ref_ltp_enu(self, *larg):
    if(self.cpt==0):
      self.cpt=1
      global mytimer
      mytimer.start()
    if int(self.stamp)!=0:self.checkdelay()
    self.stamp=time.time()
    self.string=larg[1]
    self.string=(larg[1].split())[4:7]
    self.available_string.set()

  def checkdelay(self):
    if ((time.time()-self.stamp)>=self.tole):
      self.outcpt=self.outcpt+1
      print(self.outcpt)
      self.available_outcpt.set()


class ComputeDelay(Thread):
  def __init__(self,g,i):
    Thread.__init__(self)
    self.g=g
    self.i=i

  def run(self):
    while self.i.available_outcpt.wait():
      self.g.update_lab2(i.outcpt)
      self.i.available_outcpt.clear()


class ComputeString(Thread):
  def __init__(self,g,i):
    Thread.__init__(self)
    self.g=g
    self.i=i

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
      self.g.update_lab1(tmp)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-f', '--freq', dest='freq', default=120, type=int, help="transmit frequency")
  parser.add_argument('-t', '--tole', dest='tole', default=50, type=int, help="percent tolerance")
  args = parser.parse_args()

  g=Gui(None)
  i=IvyThread('127:2010',args.freq,args.tole)
  mytimer=RepeatTimer(int(1.0/args.freq),i.checkdelay)
  c1=ComputeString(g,i)
  c2=ComputeDelay(g,i)
  c1.start()
  c2.start()
  g.mainloop()
  IvyStop()
