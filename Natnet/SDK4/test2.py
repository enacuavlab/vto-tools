#!/usr/bin/python3
from NatNetClient import NatNetClient
import time
import sys

# This program gets data from Motive Server v3, with following settings:
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
  print("------------------")
  print("receive_new_frame")
  pass

#--------------------------------------------------------------------------------
def receive_rigid_body_frame( new_id, position, rotation ):
  print("------------------")
  print("receive_rigid_body_frame")
  pass

#--------------------------------------------------------------------------------
def print_configuration(natnet_client):
  print("Connection Configuration:")
  print("  Client:          %s"% natnet_client.local_ip_address)
  print("  Server:          %s"% natnet_client.server_ip_address)
  print("  Command Port:    %d"% natnet_client.command_port)
  print("  Data Port:       %d"% natnet_client.data_port)

  if natnet_client.use_multicast:
    print("  Using Multicast")
    print("  Multicast Group: %s"% natnet_client.multicast_address)
  else:
    print("  Using Unicast")

  application_name = natnet_client.get_application_name()
  nat_net_requested_version = natnet_client.get_nat_net_requested_version()
  nat_net_version_server = natnet_client.get_nat_net_version_server()
  server_version = natnet_client.get_server_version()

  print("  NatNet Server Info")
  print("    Application Name %s" %(application_name))
  print("    NatNetVersion  %d %d %d %d"% (nat_net_version_server[0], nat_net_version_server[1], 
    nat_net_version_server[2], nat_net_version_server[3]))
  print("    ServerVersion  %d %d %d %d"% (server_version[0], server_version[1], server_version[2], server_version[3]))
  print("  NatNet Bitstream Requested")
  print("    NatNetVersion  %d %d %d %d"% (nat_net_requested_version[0], nat_net_requested_version[1],\
    nat_net_requested_version[2], nat_net_requested_version[3]))


#--------------------------------------------------------------------------------
if __name__ == "__main__":

  nc = NatNetClient()
  multicast = False
  if multicast :

    # Message ID  :   7 NAT_FRAMEOFDATA
    # Call receive_rigid_body_frame

    # MoCap Frame Begin
    # Model Marker Name + Marker Count + Marker Pos
    # Rigid Body ID + ?

    # These messages change when bodies are moved

    nc.set_client_address('0.0.0.0')
    nc.set_use_multicast(True)

  else:

    # Message ID  :   1 NAT_SERVERINFO

    # Message ID  :   5 NAT_MODELDEF

    # These messages do not change when bodies are moved

    nc.set_client_address('192.168.1.237')
    nc.set_server_address('192.168.1.231')

  nc.new_frame_listener = receive_new_frame
  nc.rigid_body_listener = receive_rigid_body_frame

  is_running = nc.run()
  if not is_running:
    print("ERROR: Could not start streaming client.")
    try:
      sys.exit(1)
    except SystemExit:
      print("...")
    finally:
      print("exiting")

  is_looping = True
  time.sleep(1)
  if nc.connected() is False:
    print("ERROR: Could not connect properly.  Check that Motive streaming is on.")
    try:
      sys.exit(2)
    except SystemExit:
      print("...")
    finally:
      print("exiting")

  print_configuration(nc)
  time.sleep(1)
  nc.send_request(nc.command_socket,nc.NAT_REQUEST_MODELDEF,"",(nc.server_ip_address,nc.command_port))

  while is_looping:
    inchars = input('Enter key \n')
    is_looping = False
    nc.shutdown()
