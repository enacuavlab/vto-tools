#!/usr/bin/env python3


'''
pip3 install pyquaternion
pip3 install open3d
Manual installation of Ivy:
    1. git clone https://gitlab.com/ivybus/ivy-python.git
    2. cd ivy-python
    3. sudo python3 setup.py install
'''

import open3d as o3d
import numpy as np
import logging
import queue

from enum import Enum
from pyquaternion import Quaternion
from ivy.std_api import *

# from paparazzi messages.xml
UNIT_COEF_ATT = 0.0139882
UNIT_COEF_POS = 0.0039063

STL_COLOR = [[0.1,0.5,0.5],[0.9,0.1,0.1]]
IVYAPPNAME = 'ivy3d'
MOTION_QUEUE=queue.Queue()

class Motion:
  def __init__(self,acid,msgtype,transf):
    self.acid=acid
    self.msgtype=msgtype
    self.transf=transf

class Mesh:
  def __init__(self,acid,msgtype,transf,mesh):
    self.model=Motion(acid,msgtype,transf)
    self.mesh=mesh

class MsgType(Enum):
  ROTORCRAFT_FP=0
  LTP_ENU=1

class Expected:
  def __init__(self,param):
   self.acid     = int(param[0])
   self.msgtype  = MsgType.ROTORCRAFT_FP if(param[1]=='ROTORCRAFT_FP') else MsgType.LTP_ENU
   self.stlfile  = param[2]
   self.stlcolor = ([float(x) for x in param[3].split(",")])


class IvyThread:
  def __init__(self,expected,expectedtab,bus):
    logging.getLogger('Ivy').setLevel(logging.ERROR)
    readymsg = '%s READY' % IVYAPPNAME
    IvyInit(IVYAPPNAME,readymsg,0,self.on_cnx,0)
    IvyStart(bus)
    if(expected):
      flag1,flag2=False,False
      for elt in expectedtab:
        if(elt.msgtype==MsgType.ROTORCRAFT_FP):flag1=True
        if(elt.msgtype==MsgType.LTP_ENU):flag2=True
    else:flag1,flag2=True,True
    if(flag1):IvyBindMsg(self.on_msg_rotorcraft_fp, '(.*ROTORCRAFT_FP.*)')
    if(flag2):IvyBindMsg(self.on_msg_ground_ref_ltp_enu, '(.*LTP_ENU.*)')

  def on_cnx(self, dum1, dum2):
#    if(dum2==2):self.stop_flag=0
    return

  def on_msg_rotorcraft_fp(self, *larg):
    mystr=larg[1].split()
    acid=int(mystr[0][6:]) if(mystr[0].startswith("replay")) else int(mystr[0])
    pos=[elt * UNIT_COEF_POS for elt in list(map(float,mystr[2:5]))]
    att=[elt * UNIT_COEF_ATT for elt in list(map(float,mystr[8:11]))]
    MOTION_QUEUE.put(Motion(acid,MsgType.ROTORCRAFT_FP,
      ((np.array([100*pos[0],100*pos[2]+14,-100*pos[1]],dtype=float)),
       (((Quaternion(axis=[1, 0, 0], degrees=att[1]))*
        (Quaternion(axis=[0, 1, 0],degrees=-att[2]))*
        (Quaternion(axis=[0, 0, 1], degrees=-att[0]))).elements))))

  def on_msg_ground_ref_ltp_enu(self, *larg):
    mystr=larg[1].split()
    acid=int(mystr[2])
    pos=[elt for elt in list(map(float,mystr[4].split(",")))]
    quat=[elt for elt in list(map(float,mystr[6].split(",")))]
    MOTION_QUEUE.put(Motion(acid,MsgType.LTP_ENU,
      ((np.array([100*pos[0],100*pos[2]+14,-100*pos[1]],dtype=float)), # y,z,-x
      (np.array([quat[0],quat[1],quat[3],-quat[2]],dtype=float)))))

def usage(argv):
  expectedtab=[]
  expected,ret=False,True
  bus='127:2010'
  if(len(argv)>1):
    fract=((len(argv)-1)%4)
    for i in range(int((len(argv)-1)/4)):
      expectedtab.append(Expected(argv[1+i*4:5+i*4]))
      expected=True
    if(fract==1):bus=argv[-1]
    if(fract>1):
      print("usage: ivy3d.py acid ROTORCRAFT_FP/LTP_ENU models/stl_sketch r,g,b ivybus:127-255:2010")
      print("ivy3d.py")
      print("ivy3d.py 255:2010")
      print("         116 ROTORCRAFT_FP 212 0.1,0.1,0.9")
      print("         116 ROTORCRAFT_FP 212 0.1,0.1,0.9 255:2010")
      print("         116 ROTORCRAFT_FP 212 0.1,0.1,0.9 115 LTP_ENU 115 0.1,0.9,0.1")
      ret=False
  return(ret,expected,expectedtab,bus)

def o3d_init():
  vis=o3d.visualization.Visualizer()
  vis.create_window(window_name=IVYAPPNAME,width=640,height=480)
  trmesh_frame=o3d.geometry.TriangleMesh.create_coordinate_frame(size=100)
  trmesh_frame.rotate(R=trmesh_frame.get_rotation_matrix_from_quaternion([0.5,0.5,0.5,-0.5]),
                      center=trmesh_frame.get_center())
  trmesh_box=o3d.geometry.TriangleMesh.create_box(width=100.0,height=1.0,depth=100.0)
  trmesh_box.rotate(R=trmesh_box.get_rotation_matrix_from_xyz((0,np.pi/2,0)),center=[0,0,0])
  trmesh_box.compute_vertex_normals()
  vis.add_geometry(trmesh_frame)
  vis.add_geometry(trmesh_box)
  return(vis)

def o3d_loop(expected,expectedtab):
  meshtab=[]
  stlcolor=0

  while (True):
    notregistered=True
    if(not MOTION_QUEUE.empty()):
      motion=MOTION_QUEUE.get()
      curr=motion.transf
      for i,elt in enumerate(meshtab):
        if((motion.acid==elt.model.acid)and(motion.msgtype==elt.model.msgtype)):
          notregistered=False
          updateFlag=False
          if any(abs(abs(curr[0][i])-abs(elt.model.transf[0][i]))>.5 for i in range(3)):
            elt.mesh.translate(curr[0],relative=False)
            elt.model.transf[0][:]=curr[0][:]
            updateFlag=True
          if any(abs(abs(curr[1][i])-abs(elt.model.transf[1][i]))>0.008 for i in range(4)):
            rot3=(Quaternion(curr[1])*((Quaternion(elt.model.transf[2])).inverse))
            elt.mesh.rotate(
              R=elt.mesh.get_rotation_matrix_from_quaternion(rot3.elements),center=elt.mesh.get_center())
            elt.model.transf[2][:]=(rot3.elements)
            elt.model.transf[1][:]=curr[1]
            updateFlag=True
          if updateFlag:vis.update_geometry(elt.mesh)
          break

      if (notregistered):
        displayflag=False
        if(expected):
          for i,elt in enumerate(expectedtab):
            if((motion.acid==elt.acid)and(motion.msgtype==elt.msgtype)):
              modelfile="models/"+elt.stlfile+".stl"
              modelcolor=elt.stlcolor
              displayflag=True
              break
        else:
          modelfile="models/"+str(motion.acid)+".stl"
          modelcolor=STL_COLOR[stlcolor]
          stlcolor=stlcolor+1
          displayflag=True
        if(displayflag):
          mesh_model=o3d.io.read_triangle_mesh(modelfile)
          mesh_model.compute_vertex_normals()
          mesh_model.paint_uniform_color(modelcolor)
          mesh_model.translate(curr[0],relative=False)
          mesh_model.rotate(
            R=mesh_model.get_rotation_matrix_from_quaternion(curr[1]),center=mesh_model.get_center())
          meshtab.append(Mesh(motion.acid,motion.msgtype,(curr[0],curr[1],curr[1]),mesh_model))
          vis.add_geometry(mesh_model)

    if not vis.poll_events():break
    vis.update_renderer()

if __name__ == '__main__':
  ret,expected,expectedtab,bus=usage(sys.argv)
  if(ret):
    thr=IvyThread(expected,expectedtab,bus)
    vis=o3d_init()
    o3d_loop(expected,expectedtab)
    vis.destroy_window()
    IvyStop()
