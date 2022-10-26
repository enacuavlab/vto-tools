#!/usr/bin/python3
import MoCapData
from threading import Thread
import socket
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
def unpack_mocap_data(data : bytes, packet_size):
  mocap_data = MoCapData.MoCapData()
  print( "MoCap Frame Begin\n-----------------" )
  data = memoryview( data )
  offset = 0
  rel_offset = 0


#--------------------------------------------------------------------------------
def data_thread_function(in_socket, stop):
  message_id_dict={}
  data=bytearray(0)
  # 64k buffer size
  recv_buffer_size=64*1024

  print("data_thread_function")
  while not stop():
    try:
      data, addr = in_socket.recvfrom( recv_buffer_size )
    except socket.error as msg:
      if not stop():
        print("ERROR: data socket access error occurred:\n  %s" %msg)
        return 1
    except  socket.herror:
      print("ERROR: data socket access herror occurred")
    except  socket.gaierror:
      print("ERROR: data socket access gaierror occurred")
    except  socket.timeout:
      print("ERROR: data socket access timeout occurred. Server not responding")
    if len( data ) > 0 :
      message_id = int.from_bytes( data[0:2], byteorder='little' )
      packet_size = int.from_bytes( data[2:4], byteorder='little' )

#      tmp_str="mi_%1.1d"%message_id
#      if tmp_str not in message_id_dict:
#        message_id_dict[tmp_str]=0
#      message_id_dict[tmp_str] += 1

#      print(message_id_dict)
#      message_id = process_message( data , print_level)
#      data=bytearray(0)
      if message_id == 7 : # NAT_FRAMEOFDATA :
        offset = 4
        offset_tmp, mocap_data = unpack_mocap_data( data[offset:], packet_size )
        offset += offset_tmp
        print("MoCap Frame: %d\n"%(mocap_data.prefix_data.frame_number))
        # get a string version of the data for output
        mocap_data_str=mocap_data.get_as_string()
        print("%s\n"%mocap_data_str)

      data=bytearray(0)


#--------------------------------------------------------------------------------
if __name__ == "__main__":

  data_sock = socket.socket( socket.AF_INET,socket.SOCK_DGRAM,0) 
  data_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  data_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton("239.255.42.99") + socket.inet_aton("0.0.0.0"))
  try:
    data_sock.bind( ("0.0.0.0", 1511) )
  except socket.error as msg:
    print("ERROR: data socket error occurred:\n%s" %msg)
    print("  Check Motive/Server mode requested mode agreement.  You requested Multicast ")

  stop_threads = False
  data_thread = Thread( target = data_thread_function, args = (data_sock, lambda : stop_threads, ))
  data_thread.start()

  is_looping = True
  while is_looping:
    inchars = input('Enter key \n')
    stop_threads = True
    is_looping = False
