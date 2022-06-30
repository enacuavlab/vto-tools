#!/usr/bin/python3
from NatNetClient import NatNetClient
import time
import sys

#--------------------------------------------------------------------------------
def receive_rigid_body_frame(rigidBodyList, stamp ):
  print("------------------")
  print("receive_rigid_body_frame")

#--------------------------------------------------------------------------------
def init():
  #nc = NatNetClient(server="127.0.0.1", rigidBodyListListener=receive_rigid_body_frame,dataPort=int(1511), commandPort=int(1510))
  nc = NatNetClient()
  nc.rigidBodyListListener=receive_rigid_body_frame
  nc.run()
  return nc,True

#--------------------------------------------------------------------------------
def stop(mythread):
  mythread.shutdown()
  sys.exit(1)

#--------------------------------------------------------------------------------
if __name__ == '__main__':
  loop = True
  threadNatnet,ret = init()
  if not ret: stop(threadNatnet)
  try:
    while loop:
      time.sleep(0.01)

  except KeyboardInterrupt:
    print("\nWe are interrupting the program\n")
    loop = False
    stop(threadNatnet)
    print("mainloop stopped")
