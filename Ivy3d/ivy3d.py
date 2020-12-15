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
import copy as copy
import logging
import string

from array import array
from enum import Enum
from pyquaternion import Quaternion
from ivy.std_api import *

IVYAPPNAME = 'ivy3d'
#IVYBUS = '127:2010'
#IVYBUS = '192.168.1.255:2010'
IVYBUS = '127:2010'

# from paparazzi messages.xml
UNIT_COEF_ATT = 0.0139882
UNIT_COEF_POS = 0.0039063

STL_COLOR = [[0.1,0.5,0.5],[0.9,0.1,0.1]]

class msgType(Enum):
  ROTORCRAFT_FP=0
  LTP_ENU=1

class Expected:
  def __init__(self,param):
   self.acid      = int(param[0])
   self.modeltype = msgType.ROTORCRAFT_FP if(param[1]=='ROTORCRAFT_FP') else msgType.LTP_ENU
   self.stlfile   = param[2]
   self.stlcolor  = ([float(x) for x in param[3].split(",")])

class Model:
  def __init__(self,acid,modeltype,transf):
    self.acid=acid
    self.modeltype=modeltype
    self.transf=transf

class Mesh:
  def __init__(self,acid,modeltype,transf,mesh):
    self.model=Model(acid,modeltype,transf)
    self.mesh=mesh

class Ivy3d:
  def __init__(self):
    self.updateModel=Model(0,0,([0,0,0],[0,0,0,0]))
    self.updated=False
    self.stop_flag=1
    logging.getLogger('Ivy').setLevel(logging.ERROR)
    readymsg = '%s READY' % IVYAPPNAME
    IvyInit(IVYAPPNAME,readymsg,0,self.on_cnx,0)
    IvyStart(IVYBUS)
    IvyBindMsg(self.on_msg_rotorcraft_fp, '(.*ROTORCRAFT_FP.*)')
    IvyBindMsg(self.on_msg_ground_ref_ltp_enu, '(.*LTP_ENU.*)')

  def on_cnx(self, dum1, dum2):
#    if(dum2==2):self.stop_flag=0
    return

  def on_msg_rotorcraft_fp(self, *larg):
    if(self.updated==False):
      self.updated=True
      mystr=larg[1].split()
      acid=int(mystr[0][6:]) if(mystr[0].startswith("replay")) else int(mystr[0])
      pos=[elt * UNIT_COEF_POS for elt in list(map(float,mystr[2:5]))]
      att=[elt * UNIT_COEF_ATT for elt in list(map(float,mystr[8:11]))]
      self.updateModel=Model(acid,msgType.ROTORCRAFT_FP,
          ((np.array([100*pos[0],100*pos[2]+14,-100*pos[1]],dtype=float)),
           (((Quaternion(axis=[1, 0, 0], degrees=att[1]))*
                   (Quaternion(axis=[0, 1, 0],degrees=-att[2]))*
                   (Quaternion(axis=[0, 0, 1], degrees=-att[0]))).elements)))

  def on_msg_ground_ref_ltp_enu(self, *larg):
    if(self.updated==False):
      self.updated=True
      mystr=larg[1].split()
      acid=int(mystr[2])
      pos=[elt for elt in list(map(float,mystr[4].split(",")))]
      quat=[elt for elt in list(map(float,mystr[6].split(",")))]
      self.updateModel=Model(acid,msgType.LTP_ENU,
          ((np.array([100*pos[0]+70,100*pos[2]+5,-100*pos[1]-300],dtype=float)), # y,z,-x
          (np.array([quat[0],quat[1],-quat[3],-quat[2]],dtype=float))))

if __name__ == '__main__':
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

  frm=Ivy3d()
  meshtab=[]
  stlcolor=0

  expectedtab=[]
  expected=False
  if(len(sys.argv)>1):
    if(((len(sys.argv)-1)%4)==0):
      for i in range(int((len(sys.argv)-1)/4)):
        expectedtab.append(Expected(sys.argv[1+i*4:5+i*4]))
        expected=True
    else:
      print("usage: ivy3d.py acid ROTORCRAFT_FP/LTP_ENU models/stl_sketch r,g,b")
      print("ivy3d.py 116 ROTORCRAFT_FP 212 0.1,0.1,0.9")
      print("ivy3d.py 116 ROTORCRAFT_FP 212 0.1,0.1,0.9 115 LTP_ENU 115 0.1,0.9,0.1")
      frm.stop_flag=False
        
  while (frm.stop_flag):
    if (frm.updated):
      acid=frm.updateModel.acid
      curr=frm.updateModel.transf
      modeltype=frm.updateModel.modeltype
      notregistered=True

      for i,elt in enumerate(meshtab):
        if((acid==elt.model.acid)and(modeltype==elt.model.modeltype)):
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
            if((acid==elt.acid)and(modeltype==elt.modeltype)):
              modelfile="models/"+elt.stlfile+".stl"
              modelcolor=elt.stlcolor
              modeltype=elt.modeltype
              displayflag=True
              break
        else:
          modelfile="models/"+str(acid)+".stl"
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
          meshtab.append(Mesh(acid,modeltype,(curr[0],curr[1],curr[1]),mesh_model))
          vis.add_geometry(mesh_model)

      frm.updated=False

    if not vis.poll_events():break
    vis.update_renderer()

  vis.destroy_window()
  IvyStop()
