#!/usr/bin/env python3

#https://courses.ideate.cmu.edu/16-455/s2020/ref/text/_modules/optitrack/csv_reader.html#CSVReader

from threading import Thread
import tkinter
import logging
import time
import csv
import collections
ColumnMapping = collections.namedtuple('ColumnMapping', ['setter', 'axis', 'column'])

from ivy.std_api import *

IVYAPPNAME = 'track2ivy'
IVYBUS = '127:2010'

class Track2ivy(tkinter.Tk):

  def on_button(self,event):
    tmp=self.scale.get()
    if(self.scale_stored == tmp):
      if self._thread is None:
        if self._stop==True:
          self._stop = False
          self._thread = Thread(target=self.run)
          self._thread.start()
      else :
        self._thread, self._stop = None, True
    else :
      self._thread, self._stop = None, True
    self.scale_stored=tmp

  def on_cnx(self, dum1, dum2):
    print(dum1,dum2)

  def on_close(self):
    if(self._thread==None) and (self._stop):
      self.destroy()
      IvyStop()
    self._thread, self._stop = None, True

  def __init__(self,parent,take):
    tkinter.Tk.__init__(self,parent)
    self.parent = parent
    self._thread, self._stop = None, True
    self.take=take
    self.grid()
    self.scale=tkinter.Scale(self, from_=0, to=take._maxitems, orient=tkinter.HORIZONTAL)
    self.scale.bind("<ButtonRelease-1>", self.on_button)
    self.scale.grid(column=0,row=0,sticky='NSEW')
    self.scale_stored=0
    self.grid_columnconfigure(0,weight=1)
    self.grid_rowconfigure(0,weight=1)
    self.minsize(width=180,height=50)
    self.resizable(True,False)
    self.title(IVYAPPNAME)
    logging.getLogger('Ivy').setLevel(logging.NOTSET)
    readymsg = '%s READY' % IVYAPPNAME
    IvyInit(IVYAPPNAME,readymsg,0,self.on_cnx,0)
    IvyStart(IVYBUS)
    self.protocol("WM_DELETE_WINDOW", self.on_close)
    self.mainloop()

  def run(self):
    i=self.scale.get()
    while((i<self.take._maxitems)and(not self._stop)):
      for body in self.take.rigid_bodies.values():
        if body.positions[i]==None or body.rotations[i]==None:break
        # Y, X, Z 
        msg="ground GROUND_REF "+str(body.label.partition("_")[2])+\
           " LTP_ENU %f,%f,%f"%(body.positions[i][0],-body.positions[i][2],body.positions[i][1])+\
           " 0.,0.,0. %f,%f,%f,%f"\
           %(body.rotations[i][3],body.rotations[i][0],-body.rotations[i][2],-body.rotations[i][1])+\
           " 0.,0.,0. 0."
        IvySendMsg(msg)
      i=i+4
      time.sleep(1/30.)    
      self.scale.set(i)
      #time.sleep(1/self.take.frame_rate)    
#    IvyStop()


class RigidBody(object):
  def __init__(self, label, ID):
    self.label     = label
    self.ID        = ID
    self.positions = list()
    self.rotations = list()
    self.times     = list()
    return

  def _add_frame(self, t):
    self.times.append(t)
    self.positions.append(None)
    self.rotations.append(None)

  def _set_position( self, frame, axis, value ):
    if value != '':
      if self.positions[frame] is None:
        self.positions[frame] = [0.0,0.0,0.0]
      self.positions[frame][axis] = float(value)

  def _set_rotation( self, frame, axis, value ):
    if value != '':
      if self.rotations[frame] is None:
        self.rotations[frame] = [0.0,0.0,0.0,0.0]
      self.rotations[frame][axis] = float(value)


class Take_V1_23(object):
  def __init__(self,path):
    self.frame_rate    = 120.0
    self.rigid_bodies = dict()
    self._raw_info    = dict()
    self._raw_types   = list()
    self._raw_labels  = list()
    self._raw_fields  = list()
    self._raw_axes    = list()
    self._ignored_labels  = set()
    self._column_map = list() 
    with open(path, 'r') as file_handle:
      csv_stream = csv.reader(file_handle)
      self._read_header(csv_stream)
      self._read_data(csv_stream)        
      self._maxitems=0
      for body in self.rigid_bodies.values():
        if len(body.times)>self._maxitems:self._maxitems=len(body.times)

  def _read_header(self,stream):
    line1 = next(stream)
    assert line1[0] == 'Format Version', "Unrecognized header cell: %s" % line1[0]
    format = line1[1]
    assert (format == '1.23'),"Unsupported format version: %s"%line1[1]
    line2 = next(stream)
    assert len(line2) == 0, 'Expected blank second header line, found %s.' % line2
    line3 = next(stream)
    self._raw_types = line3[2:]
    all_types = set( self._raw_types )
    supported_types = set(['Rigid Body', 'Rigid Body Marker', 'Marker'])
    assert all_types.issubset(supported_types),\
            'Unsupported object type found in header line 3: %s'%all_types
    line4 = next(stream)
    self._raw_labels = line4[2:]
    line5 = next(stream)
    line6 = next(stream)
    self._raw_fields = line6[2:]
    line7 = next(stream)
    self._raw_axes = line7[2:]
    for col,asset_type,label,ID,field,axis in zip(range(len(self._raw_types)), self._raw_types, \
                                  self._raw_labels,line5[2:], self._raw_fields, self._raw_axes): 
      if asset_type == 'Rigid Body':
       if label in self.rigid_bodies:
         body = self.rigid_bodies[label]
       else:
         body = RigidBody(label,ID)
         self.rigid_bodies[label] = body
       if field == 'Rotation':
         axis_index = {'X':0, 'Y':1, 'Z':2, 'W': 3}[axis]
         setter = body._set_rotation
         self._column_map.append(ColumnMapping(setter, axis_index, col))
       elif field == 'Position':
         axis_index = {'X':0, 'Y':1, 'Z':2}[axis]
         setter = body._set_position
         self._column_map.append(ColumnMapping(setter, axis_index, col))

  def _read_data(self, stream):
    for row_num, row in enumerate(stream):
      frame_num = int(row[0])
      frame_t   = float(row[1])
      values    = row[2:]
      for body in self.rigid_bodies.values():
        body._add_frame(frame_t)
      for mapping in self._column_map:
        mapping.setter( row_num, mapping.axis, values[mapping.column] )

if __name__ == '__main__':
  Track2ivy(None,Take_V1_23(sys.argv[1]))
