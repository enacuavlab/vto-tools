#!/usr/bin/python3

import socket
import select
import struct
import threading
import signal
import time
import datetime
import math
import numpy as np
from proxy_common import *
from vector_fields import spheric_geo_fence, ParametricTrajectory, Controller

GROUND2MAVS=4300
TELEMETRY=4246

FCROTOR_INDEX=15
NAV_HEADING_INDEX=41

DL_VALUE=31
GET_SETTING=16
ROTORCRAFT_FP=147
ROTORCRAFT_NAV_STATUS=159
INS=198

I2P = 1. / 2**8    # integer to position
I2V = 1. / 2**19   # integer to velocity
I2W = 1. / 2**12   # integer to angle


class aircraft(object):
  def __init__(self):
    self.validity=False
    self.position=np.zeros(3)
    self.velocity=np.zeros(3)
    self.W=np.zeros(3)
    self.rate=0.
    self.store=0.
    self.validity=False
    self.lock = threading.Lock()
    self.fcrotor_started = False

  def set(self,position,velocity):
    self.lock.acquire()
    self.position=position
    self.velocity=velocity
    curr=datetime.datetime.now().timestamp()
    if self.validity: self.rate=curr-self.store
    self.store=curr
    self.validity=True
    self.lock.release()

  def get(self):
    self.lock.acquire()
    position=self.position
    velocity=self.velocity
    validity=self.validity
    rate=self.rate
    self.lock.release()
    return(validity,position,velocity,rate)


class inputs(threading.Thread):
  def __init__(self,ac,outs):
    threading.Thread.__init__(self)
    self.ac = ac
    self.outs = outs
    self.cur_block = -1
    self.shutdown_flag = threading.Event()
    self.running = True
    self.streams = {}
    for port in [TELEMETRY,BOARDCLI,GROUND2MAVS]:
       sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       sock.bind(('localhost', port))
       self.streams[sock] = (port,PprzTransport())


  def stop(self):
    for s in self.sockets: s.close()
    self.running = False
    self.server.close()

  def run(self):
    try:
      sockets = self.streams.keys()
      while self.running  and not self.shutdown_flag.is_set():
        try:
          (readable, writable, exceptional) = select.select(sockets, [], [])
          for s in readable:
            (data, address) = s.recvfrom(1024)
            port,transport = self.streams[s]
            for c in data:
              if not isinstance(c, bytes): c = struct.pack("B",c)
              if transport.parse_byte(c):
                # STX + length + sender_id + receiver + comp/class + msg_id + data + ck_a + ck_b
                (start,length,sender,receiver,comp,msgid) = struct.unpack('BBBBBB',transport.buf[0:6])
                if ((msgid == ROTORCRAFT_FP) and (comp == 0x01)): self.rotorcraft_fp_cb(transport.buf)
                if ((msgid == ROTORCRAFT_NAV_STATUS) and (comp == 0x01)): self.rotorcraft_nav_status_cb(transport.buf)
                #if ((msgid == REMOTE_GPS_LOCAL) and (comp == 0x02)): self.remote_gps_local_cb(transport.buf)
                if ((msgid == DL_VALUE) and (comp == 0x01)): self.fcrotor_set_cb(transport.buf)
                if ((msgid == 0x01) and (comp == 0x00)): self.ground2imavs_cb(transport.buf)
        except socket.timeout:
          pass
    except StopIteration:
      pass

  def ground2imavs_cb(self,buf):
    offset=6
    position=np.zeros(3);velocity=np.zeros(3)
    acid = struct.unpack('B',buf[offset:offset+1]);offset+=1; 
    (position[1],position[0],position[2],velocity[1],velocity[0],velocity[2]) = struct.unpack('ffffff',buf[offset:offset+24])
    self.ac.set(position,velocity)
    #print('GROUND2IMAV %f %f %f %f %f %f' % (position[1],position[0],position[2],velocity[1],velocity[0],velocity[2]))

  def fcrotor_set_cb(self,buf):
    offset=6
    index = struct.unpack('B',buf[offset:offset+1]);offset+=1; 
    if (index[0] == FCROTOR_INDEX):
      value = struct.unpack('f',buf[offset:offset+4])
      if value[0] == 0.0: self.ac.fcrotor_started = False
      else: self.ac.fcrotor_started = True
      #print(self.ac.fcrotor_started)

  def remote_gps_local_cb(self,buf):
    offset=6
    position=np.zeros(3);velocity=np.zeros(3);W=np.zeros(3)
    (acid,pad) = struct.unpack('BB',buf[offset:offset+2]);offset+=2; 
    (position[1],position[0],position[2],velocity[1],velocity[0],velocity[2]) = struct.unpack('ffffff',buf[offset:offset+24])
    self.ac.set(position,velocity)
    #print('REMOTE %d %f %f %f %f %f %f' % (pad,position[1],position[0],position[2],velocity[1],velocity[0],velocity[2]))

  def rotorcraft_nav_status_cb(self,buf):
    offset=6
    (block_time,stage_time) = struct.unpack('HH',buf[offset:offset+4]);offset+=4
    (dist_home,dist_wp) = struct.unpack('ff',buf[offset:offset+8]);offset+=8
    (cur_block,cur_stage,horiz_mode) = struct.unpack('BBB',buf[offset:offset+3])
    if (self.cur_block != cur_block): 
      self.cur_block = cur_block
      self.outs.request_setting = True

  def rotorcraft_fp_cb(self,buf):
    offset=6
    position=np.zeros(3);velocity=np.zeros(3);W=np.zeros(3)
    position[1] = I2P*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset+=4 # east
    position[0] = I2P*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset+=4 # north
    position[2] = I2P*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset+=4 # up
    velocity[1] = I2V*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset+=4 # veast
    velocity[0] = I2V*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset+=4 # vnorth
    velocity[2] = I2V*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset+=4 # vup
    phi         = I2W*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset+=4 # phi
    theta       = I2W*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset+=4 # theta
    W[2]        = I2W*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset+=4 # psi
    self.ac.set(position,velocity)
    #print('ROT %f %f %f %f %f %f' % (position[0],position[1],position[2],velocity[0],velocity[1],velocity[2]))

  def ins_cb(self,buf):
    offset=6
    position=np.zeros(3);velocity=np.zeros(3)
    position[0] = I2P*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset=offset+4 # ins_x
    position[1] = I2P*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset=offset+4 # ins_y
    position[2] = I2P*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset=offset+4 # ins_z
    velocity[0] = I2V*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset=offset+4 # ins_xd
    velocity[1] = I2V*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset=offset+4 # ins_yd
    velocity[2] = I2V*float(int.from_bytes(buf[offset:offset+4], byteorder='little', signed=True));offset=offset+4 # ins_zd
    self.ac.set(position,velocity)
    #print('INS %f %f %f %f %f %f' % (position[0],position[1],position[2],velocity[0],velocity[1],velocity[2]))

  def desired_set_point_cb(self,buf):
    offset=6
    (acid,flag) = struct.unpack('BB',buf[offset:offset+2]);offset+=2; 
    (ux,uy,uz) = struct.unpack('fff',buf[offset:offset+12])



class outputs(threading.Thread):
  def __init__(self,ac):
    threading.Thread.__init__(self)
    self.ac = ac
    self.shutdown_flag = threading.Event()
    self.running = True
    self.request_setting = True
    self.addr_out = ('localhost', BOARDSERV)
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.parametric = self.init_parametric_circle()
    self.gvf_parameter = 0

  def request_setting_cmd(self,sock,addr_out):
    acid = 114
    payload  = struct.pack('BB',FCROTOR_INDEX,acid)
    msg = struct.pack("BBBBBB", STX, 10, 0, 0, 2, GET_SETTING) + payload
    (ck_a, ck_b) = calculate_checksum(msg)
    msg += struct.pack('BB', ck_a, ck_b)
    sock.sendto(msg, addr_out)
    self.request_setting = False
    #print("request_setting")

  def run(self):
    try:
      V_des = np.zeros(3)
      while self.running  and not self.shutdown_flag.is_set():
        (validity,position,velocity,rate)=self.ac.get()
        if validity: self.send_highrate_pos(position,velocity)
        if validity and self.ac.fcrotor_started:
          V_des = spheric_geo_fence(position[0], position[1], position[2], x_source=0., y_source=0., z_source=0., strength=-0.07)
          (V_des_increment,self.gvf_parameter) = self.run_parametric_circle(position,self.gvf_parameter)
          V_des += V_des_increment
          nav_heading = self.compute_heading(V_des)
          self.accelerate(velocity,V_des,nav_heading)
          print(V_des)
        if (self.request_setting == True): 
          self.request_setting_cmd(self.sock,self.addr_out)
          self.request_setting = False
        time.sleep(rate) # 0.125
    except StopIteration:
      pass

  def compute_heading(self,V_des):
    return ((1.5707963267948966-math.atan2(V_des[0],V_des[1]))*2**12)

  def accelerate(self,velocity,V_des,heading):
    err = V_des - velocity
    acc = err*1.6 
    self.send_command(acc[0],acc[1],-acc[2],1,heading) # 3D
    #self.send_command(acc[0],acc[1],2,0,heading) # Z is fixed 

  def send_command(self,ux,uy,uz,flag,heading):
    acid = 114
    payload  = struct.pack('BB',acid,flag)
    payload += struct.pack('fff',ux,uy,uz)
    msg = struct.pack("BBBBBB", STX, 22, 0, 0, 2, DESIRED_SETPOINT) + payload
    (ck_a, ck_b) = calculate_checksum(msg)
    msg += struct.pack('BB', ck_a, ck_b)
    self.sock.sendto(msg, self.addr_out)

    payload  = struct.pack('BB',NAV_HEADING_INDEX,acid)
    payload += struct.pack('f',heading)
    msg = struct.pack("BBBBBB", STX, 14, 0, 0, 2, SETTING) + payload
    (ck_a, ck_b) = calculate_checksum(msg)
    msg += struct.pack('BB', ck_a, ck_b)
    self.sock.sendto(msg, self.addr_out)

  def send_highrate_pos(self,pos,vel):
    acid = 114
    payload  = struct.pack('BB',acid,0)
    payload += struct.pack('ffffffff',pos[1],pos[0],pos[2],vel[1],vel[0],vel[2],0.,0.)
    msg = struct.pack("BBBBBB", STX, 42, 0, 0, 2, REMOTE_GPS_LOCAL) + payload
    (ck_a, ck_b) = calculate_checksum(msg)
    msg += struct.pack('BB', ck_a, ck_b)
    self.sock.sendto(msg, self.addr_out)
    #print("HR %d %f %f %f %f %f %f" % (0,pos[1],pos[0],pos[2],vel[1],vel[0],vel[2]))

  def stop(self):
    self.running = False

  def init_parametric_circle(self):
    ex = 0 ; ey = 0 ; ealpha = 0 ; ea = 1.1 ; eb = 1.1
    ctr = Controller(L=1e-1,beta=1e-2,k1=1e-3,k2=1e-3,k3=1e-3,ktheta=0.5,s=0.80)
    traj_parametric = ParametricTrajectory(XYZ_off=np.array([0.,0.,2.5]),
                                                        XYZ_center=np.array([1.3, 1.3, -0.6]),
                                                        XYZ_delta=np.array([0., np.pi/2, 0.]),
                                                        XYZ_w=np.array([1,1,1]),
                                                        alpha=0.,
                                                        controller=ctr)
    return(traj_parametric)


  def run_parametric_circle(self,position,gvf_parameter):
    V_des_increment,uw = self.parametric.get_vector_field(position[0],position[1],position[2],gvf_parameter)
    gvf_parameter += -uw[0]*0.1 #dt
    return(V_des_increment,gvf_parameter)



if __name__ == '__main__':

  ac = aircraft()
  outs=outputs(ac)
  streams = []
  streams.append(outs)
  streams.append(inputs(ac,outs))

  for thread in streams: thread.start()
  try:
    while True:
      time.sleep(2)
  except KeyboardInterrupt:
    for thread in streams:
      thread.shutdown_flag.set()
      thread.join()
