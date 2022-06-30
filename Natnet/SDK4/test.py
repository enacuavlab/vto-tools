#!/usr/bin/python3
from NatNetClient import NatNetClient
import time
import sys

#--------------------------------------------------------------------------------
def receive_new_frame(data_dict):
  print("------------------")
  print("receive_new_frame")

#--------------------------------------------------------------------------------
def receive_rigid_body_frame( new_id, position, rotation ):
  print("------------------")
  print("receive_rigid_body_frame")

#--------------------------------------------------------------------------------
def init_default_multicast():
  ret=False
  nc = NatNetClient()
  nc.set_client_address('0.0.0.0')
  nc.rigid_body_listener = receive_rigid_body_frame
  nc.new_frame_listener = receive_new_frame
  if(nc.run()):ret=True 
  return nc,ret

#--------------------------------------------------------------------------------
def init_unicast():
  ret=False
  nc = NatNetClient()
  nc.set_use_multicast(False)
  nc.set_client_address('0.0.0.0')
  nc.set_server_address('192.168.1.231')
  nc.rigid_body_listener = receive_rigid_body_frame
  nc.new_frame_listener = receive_new_frame
  if(nc.run()):
    print("["+nc.get_application_name()+"]")
    print(nc.get_server_version())
    print(nc.get_nat_net_version_server())
    print(nc.get_nat_net_requested_version())
    print(nc.set_nat_net_version(3,0))

#    nc.send_request(nc.command_socket, nc.NAT_REQUEST_MODELDEF,"",(nc.server_ip_address,nc.command_port))
#    nc.send_request(nc.command_socket, nc.NAT_CONNECT,"",(nc.server_ip_address,nc.command_port))
#    nc.send_request(nc.command_socket, nc.NAT_KEEPALIVE,"",(nc.server_ip_address,nc.command_port))
#    nc.send_request(nc.command_socket, nc.NAT_REQUEST_FRAMEOFDATA,"",(nc.server_ip_address,nc.command_port))

    ret=True 
  return nc,ret

#--------------------------------------------------------------------------------
def stop(mythread):
  mythread.shutdown()
  sys.exit(1)

#--------------------------------------------------------------------------------
if __name__ == '__main__':
  loop = True
#  threadNatnet,ret = init_default_multicast()
  threadNatnet,ret = init_unicast()
  if not ret: stop(threadNatnet)
  try:
    while loop:
      time.sleep(0.01)

  except KeyboardInterrupt:
    print("\nWe are interrupting the program\n")
    loop = False
    stop(threadNatnet)
    print("mainloop stopped")
