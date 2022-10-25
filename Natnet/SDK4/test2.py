#!/usr/bin/python3
from NatNetClient import NatNetClient
import time
import sys

# This program gets data from Motive Server v3, with following settins:
# Local Interface : 192.168.1.231
# Transmission Type : Multicast
# Labeled Markers : On
# Unlabeled Markers : On
# Asset Markers : On
# Rigid Bodies : On
# ...
# Command Port : 1510
# Data Port : 1511
# Multicast Interface : 239.255.42.99

#--------------------------------------------------------------------------------
def receive_new_frame(data_dict):
  #print("------------------")
  #print("receive_new_frame")
  pass

#--------------------------------------------------------------------------------
def receive_rigid_body_frame( new_id, position, rotation ):
  #print("------------------")
  #print("receive_rigid_body_frame")
  pass

#--------------------------------------------------------------------------------
def init_multicast():
  ret=False
  nc = NatNetClient()
  nc.set_client_address('0.0.0.0')
  nc.rigid_body_listener = receive_rigid_body_frame
  nc.new_frame_listener = receive_new_frame
  if(nc.run()):ret=True 
  return nc,ret

#--------------------------------------------------------------------------------
def stop(mythread):
  mythread.shutdown()
  sys.exit(1)

#--------------------------------------------------------------------------------
if __name__ == '__main__':
  loop = True
  threadNatnet,ret = init_multicast()
  if not ret: stop(threadNatnet)
  try:
    while loop:
      time.sleep(0.01)

  except KeyboardInterrupt:
    print("\nWe are interrupting the program\n")
    loop = False
    stop(threadNatnet)
    print("mainloop stopped")
