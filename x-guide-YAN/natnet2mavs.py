#!/usr/bin/python3

import socket
import struct
import threading
import time

import datetime
from collections import deque
import argparse


DATAPORT=1511
MULTICASTADDR='239.255.42.99'

NB_SAMPLES=4

NAT_FRAMEOFDATA = 7


GROUND2MAVSPORT=4300
GROUND2MAVS=1
STX = 0x99

Vector3 = struct.Struct( '<fff' )
Quaternion = struct.Struct( '<ffff' )
FloatValue = struct.Struct( '<f' )


class MocapInterface(threading.Thread):
  def __init__(self,ac):
    threading.Thread.__init__(self)
    self.shutdown_flag = threading.Event()
    self.running = True
    self.id_dict = dict(ac)
    self.track = dict([(ac_id, deque()) for ac_id in self.id_dict.keys()])
    self.rigidBodyList = []
    self.mavSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.mavAddr = ('localhost', GROUND2MAVSPORT)
    self.dataSocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
    self.dataSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.dataSocket.bind( ('', DATAPORT) )
    mreq = struct.pack("4sl", socket.inet_aton(MULTICASTADDR), socket.INADDR_ANY)
    self.dataSocket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    self.curr = datetime.datetime.now().timestamp()

  def stop(self):
    self.running = False

  def run(self):
    try:
      while self.running  and not self.shutdown_flag.is_set():
       self.dataSocket.settimeout(0.01)
       while True:
         try:
           data, addr = self.dataSocket.recvfrom( 32768 )      # 32k byte buffer size
           if( len( data ) >= 4): self.processMessage( data )
         except socket.timeout:
           pass
    except StopIteration:
      pass

  def processMessage(self,data):
    messageID = int.from_bytes( data[0:2], byteorder='little' )
    #print( "Message ID:", messageID )
    packetSize = int.from_bytes( data[2:4], byteorder='little' )
    #print( "Packet Size:", packetSize )
    if not len( data ) - 4 >= packetSize: return
    offset = 4
    if( messageID == NAT_FRAMEOFDATA ): self.unpackMocapData( data[offset:] )

  def unpackMocapData(self,data):
    data = memoryview( data )
    offset = 0
    frameNumber = int.from_bytes( data[offset:offset+4], byteorder='little' )
    offset += 4
    #print( "Frame #:", frameNumber )
    markerSetCount = int.from_bytes( data[offset:offset+4], byteorder='little' )
    offset += 4
    #print( "Marker Set Count:", markerSetCount )
    for i in range( 0, markerSetCount ):
      modelName, separator, remainder = bytes(data[offset:]).partition( b'\0' )
      offset += len( modelName ) + 1
      #print( "Model Name:", modelName.decode( 'utf-8' ) )
      markerCount = int.from_bytes( data[offset:offset+4], byteorder='little' )
      offset += 4
      #print( "Marker Count:", markerCount )
      for j in range( 0, markerCount ):
        pos = Vector3.unpack( data[offset:offset+12] )
        offset += 12
        #print( "\tMarker", j, ":", pos[0],",", pos[1],",", pos[2] )
    unlabeledMarkersCount = int.from_bytes( data[offset:offset+4], byteorder='little' )
    offset += 4
    #print( "Unlabeled Markers Count:", unlabeledMarkersCount )
    for i in range( 0, unlabeledMarkersCount ):
      pos = Vector3.unpack( data[offset:offset+12] )
      offset += 12
      #print( "\tMarker", i, ":", pos[0],",", pos[1],",", pos[2] )
    rigidBodyCount = int.from_bytes( data[offset:offset+4], byteorder='little' )
    offset += 4
    #print( "Rigid Body Count:", rigidBodyCount )
    for i in range( 0, rigidBodyCount ): offset += self.unpackRigidBody( data[offset:] )
    self.send2mav()

  def unpackRigidBody(self,data):
    offset = 0
    id = int.from_bytes( data[offset:offset+4], byteorder='little' )
    offset += 4
    #print("ID:", id )
    pos = Vector3.unpack( data[offset:offset+12] )
    offset += 12
    #print( "\tPosition:", pos[0],",", pos[1],",", pos[2] )
    rot = Quaternion.unpack( data[offset:offset+16] )
    offset += 16
    #print( "\tOrientation:", rot[0],",", rot[1],",", rot[2],",", rot[3] )
    markerError, = FloatValue.unpack( data[offset:offset+4] )
    offset += 4
    #print( "\tMarker Error:", markerError )
    param, = struct.unpack( 'h', data[offset:offset+2] )
    trackingValid = ( param & 0x01 ) != 0
    offset += 2
    #print( "\tTracking Valid:", 'True' if trackingValid else 'False' )
    self.rigidBodyList.append((id, pos, trackingValid))
    return offset

  def send2mav(self):
    for (ac_id,pos,valid) in self.rigidBodyList:
      if not valid:
        continue
      i = str(ac_id)
      if i not in self.id_dict.keys():
        continue
      stamp = datetime.datetime.now().timestamp()
      self.store_track(i, pos, stamp)
      vel=self.compute_velocity(i)
      tmp = stamp - self.curr
      self.curr = stamp
      print(ac_id,tmp)

#    payload  = struct.pack('B',ac_id)
#    payload += struct.pack('ffffff',pos[0],pos[1],pos[2],vel[0],vel[1],vel[2])
#    msg = struct.pack("BBBBBB", STX, 33, 0, 0, 0, GROUND2MAVS) + payload
#    (ck_a, ck_b) = calculate_checksum(msg)
#    msg += struct.pack('BB', ck_a, ck_b)
#    mavSocket.sendto(msg, mavAddr)
#    print(pos[0],pos[1],pos[2])

  def store_track(self,ac_id, pos, t):
    if ac_id in self.id_dict.keys():
      self.track[ac_id].append((pos, t))
      if len(self.track[ac_id]) > NB_SAMPLES:
        self.track[ac_id].popleft()

  def compute_velocity(self,ac_id):
    vel = [ 0., 0., 0. ]
    if len(self.track[ac_id]) >= NB_SAMPLES:
      nb = -1
      for (p2, t2) in self.track[ac_id]:
        nb = nb + 1
        if nb == 0:
          p1 = p2
          t1 = t2
        else:
          dt = t2 - t1
          if dt < 1e-5:
            continue
          vel[0] += (p2[0] - p1[0]) / dt
          vel[1] += (p2[1] - p1[1]) / dt
          vel[2] += (p2[2] - p1[2]) / dt
          p1 = p2
          t1 = t2
      if nb > 0:
        vel[0] /= nb
        vel[1] /= nb
        vel[2] /= nb
    return vel
  
  def calculate_checksum(msg):
    ck_a = 0
    ck_b = 0
    for c in msg[1:]:
      if isinstance(c, str): c = struct.unpack("<B", c)[0]
      ck_a = (ck_a + c) % 256
      ck_b = (ck_b + ck_a) % 256
    return ck_a, ck_b


if __name__ == '__main__':
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-ac', action='append', nargs=2,
                    metavar=('rigid_id','ac_id'), help='pair of rigid body and A/C id (multiple possible)')
  args = parser.parse_args()
  if args.ac is None:
    print("At least one pair of rigid boby / AC id must be declared")
    exit()

  thread = MocapInterface(args.ac)
  thread.start()
  try:
    while True:
      time.sleep(2)
  except KeyboardInterrupt:
    thread.shutdown_flag.set()
    thread.join()
