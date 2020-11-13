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

from pyquaternion import Quaternion
from ivy.std_api import *

IVYAPPNAME = 'ivy3d'
#IVYBUS = '127:2010'
IVYBUS = '192.168.1.255:2010'

# from paparazzi messages.xml
UNIT_COEF_ATT = 0.0139882
UNIT_COEF_POS = 0.0039063

STL_COLOR = [[0.1,0.5,0.5],[0.9,0.1,0.1]]

class Model:
  def __init__(self,acid,transf):
    self.acid=acid
    self.transf=transf

class Mesh:
  def __init__(self,acid,transf,mesh):
    self.model=Model(acid,transf)
    self.mesh=mesh


class Ivy3d:
  def __init__(self):
    self.updateModel=Model(0,([0,0,0],[0,0,0,0]))
    self.updated=False
    self.stop_flag=1

    logging.getLogger('Ivy').setLevel(logging.ERROR)
#    logging.getLogger('Ivy').setLevel(logging.NOTSET)
    readymsg = '%s READY' % IVYAPPNAME
    IvyInit(IVYAPPNAME,readymsg,0,self.on_cnx,0)
    IvyStart(IVYBUS)
#    IvyBindMsg(self.on_msg_rotorcraft_fp, '(.*ROTORCRAFT_FP.*)')
    IvyBindMsg(self.on_msg_ground_ref_ltp_enu, '(.*LTP_ENU.*)')

  def on_cnx(self, dum1, dum2):
#    if(dum2==2):self.stop_flag=0
    return

  def on_msg_rotorcraft_fp(self, *larg):
    mystr=larg[1].split()
#    print(mystr)
    acid=int(mystr[0][6:]) if(mystr[0].startswith("replay")) else int(mystr[0])
    pos=[elt * UNIT_COEF_POS for elt in list(map(float,mystr[2:5]))]
    att=[elt * UNIT_COEF_ATT for elt in list(map(float,mystr[8:11]))]
    self.updateModel=Model(acid,
        ((np.array([100*pos[0],100*pos[2]+14,-100*pos[1]],dtype=float)),
         (((Quaternion(axis=[1, 0, 0], degrees=att[1]))*
                 (Quaternion(axis=[0, 1, 0],degrees=-att[2]))*
                 (Quaternion(axis=[0, 0, 1], degrees=-att[0]))).elements)))
    self.updated=True

  def on_msg_ground_ref_ltp_enu(self, *larg):
    mystr=larg[1].split()
#    print(mystr)
    acid=int(mystr[2])
    pos=[elt for elt in list(map(float,mystr[4].split(",")))]
    quat=[elt for elt in list(map(float,mystr[6].split(",")))]
    self.updateModel=Model(acid,
        ((np.array([100*pos[0]+70,100*pos[2]+5,-100*pos[1]-300],dtype=float)), # y,z,-x
        (np.array([quat[0],quat[1],-quat[3],-quat[2]],dtype=float))))
    self.updated=True


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
  while (frm.stop_flag):

    if frm.updated:
      frm.updated=False
      acid=frm.updateModel.acid
      curr=frm.updateModel.transf
    
      notregistered=True
      for i,elt in enumerate(meshtab):
        if(acid==elt.model.acid):
          notregistered=False
          updateFlag=False
          if any(abs(abs(curr[0][i])-abs(elt.model.transf[0][i]))>.5 for i in range(3)):
            elt.mesh.translate(curr[0],relative=False)
            elt.model.transf[0][:]=curr[0][:]
            updateFlag=True
          if any(abs(abs(curr[1][i])-abs(elt.model.transf[1][i]))>0.008 for i in range(4)):
            #print("updateRot")
            rot3=(Quaternion(curr[1])*((Quaternion(elt.model.transf[2])).inverse))
            elt.mesh.rotate(
              R=elt.mesh.get_rotation_matrix_from_quaternion(rot3.elements),center=elt.mesh.get_center())
            elt.model.transf[2][:]=(rot3.elements)
            elt.model.transf[1][:]=curr[1]
            updateFlag=True
          if updateFlag:vis.update_geometry(elt.mesh)
          break
  
      if notregistered:
        #print("register")
        mesh_model=o3d.io.read_triangle_mesh(str(acid)+".stl")
        mesh_model.compute_vertex_normals()
        mesh_model.paint_uniform_color(STL_COLOR[stlcolor])
        stlcolor=stlcolor+1
        mesh_model.translate(curr[0],relative=False)
        mesh_model.rotate(
          R=mesh_model.get_rotation_matrix_from_quaternion(curr[1]),center=mesh_model.get_center())
        meshtab.append(Mesh(acid,(curr[0],curr[1],curr[1]),mesh_model))
        vis.add_geometry(mesh_model)

    if not vis.poll_events():break
    vis.update_renderer()

  vis.destroy_window()
  IvyStop()
