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
#  nc.set_client_address('0.0.0.0')
  nc.set_server_address('192.168.1.231')

  nc.set_client_address('192.168.1.237')
  nc.data_port = 1513

  nc.rigid_body_listener = receive_rigid_body_frame
  nc.new_frame_listener = receive_new_frame
  if(nc.run()):
    time.sleep(1)
    if(not nc.connected()): stop(nc)

    application_name = nc.get_application_name()
    nat_net_requested_version = nc.get_nat_net_requested_version()
    nat_net_version_server = nc.get_nat_net_version_server()
    server_version = nc.get_server_version()

    print("  NatNet Server Info")
    print("    Application Name %s" %(application_name))
    print("    NatNetVersion  %d %d %d %d"% (nat_net_version_server[0], nat_net_version_server[1], nat_net_version_server[2], nat_net_version_server[3]))
    print("    ServerVersion  %d %d %d %d"% (server_version[0], server_version[1], server_version[2], server_version[3]))
    print("  NatNet Bitstream Requested")
    print("    NatNetVersion  %d %d %d %d"% (nat_net_requested_version[0], nat_net_requested_version[1],\
       nat_net_requested_version[2], nat_net_requested_version[3]))

    nc.set_print_level(1)
    print("Level : ",nc.get_print_level())

#    nc.send_request(nc.command_socket, nc.NAT_REQUEST_MODELDEF,"",(nc.server_ip_address,nc.command_port))
#    nc.send_request(nc.command_socket, nc.NAT_CONNECT,"",(nc.server_ip_address,nc.command_port))
#    nc.send_request(nc.command_socket, nc.NAT_KEEPALIVE,"",(nc.server_ip_address,nc.command_port))
#    nc.send_request(nc.command_socket, nc.NAT_REQUEST_FRAMEOFDATA,"",(nc.server_ip_address,nc.command_port))

    nc.SendMessageAndWait("SubscribeToData,RigidBody,Building_884")

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
