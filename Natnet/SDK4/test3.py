#!/usr/bin/python3
import MoCapData
from threading import Thread
import struct
import socket
import time
import sys

# This programs aims to get the markers position for the rigid body : Building


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
Vector3 = struct.Struct( '<fff' )

#--------------------------------------------------------------------------------
def unpack_marker_set_data(data, packet_size):
  marker_set_data=MoCapData.MarkerSetData()
  offset = 0
  # Marker set count (4 bytes)
  marker_set_count = int.from_bytes( data[offset:offset+4], byteorder='little' )
  offset += 4
  #print( "Marker Set Count:", marker_set_count )

  print(marker_set_count)
  for i in range( 0, marker_set_count ):
    marker_data = MoCapData.MarkerData()
    # Model name
    model_name, separator, remainder = bytes(data[offset:]).partition( b'\0' )
    offset += len( model_name ) + 1
    print( "Model Name      : ", model_name.decode( 'utf-8' ) )
    marker_data.set_model_name(model_name)
    # Marker count (4 bytes)
    marker_count = int.from_bytes( data[offset:offset+4], byteorder='little' )
    offset += 4
    #print( "Marker Count    : ", marker_count )

    for j in range( 0, marker_count ):
      pos = Vector3.unpack( data[offset:offset+12] )
      offset += 12
      #print( "\tMarker %3.1d : [%3.2f,%3.2f,%3.2f]"%( j, pos[0], pos[1], pos[2] ))
      marker_data.add_pos(pos)

    marker_set_data.add_marker_data(marker_data)

  return marker_set_data

#--------------------------------------------------------------------------------
def unpack_frame_prefix_data(data):
  offset = 0
  frame_number = int.from_bytes( data[offset:offset+4], byteorder='little' )
  offset += 4
  #print( "Frame #:", frame_number )
  frame_prefix_data=MoCapData.FramePrefixData(frame_number)
  return offset, frame_prefix_data

#--------------------------------------------------------------------------------
def unpack_mocap_data(data : bytes, packet_size):
  mocap_data = MoCapData.MoCapData()
  data = memoryview( data )
  offset = 0
  rel_offset = 0

  rel_offset, frame_prefix_data = unpack_frame_prefix_data(data[offset:])
  offset += rel_offset
  mocap_data.set_prefix_data(frame_prefix_data)
  frame_number = frame_prefix_data.frame_number

  marker_set_data = unpack_marker_set_data(data[offset:], (packet_size - offset))
  mocap_data.set_marker_set_data(marker_set_data)

  return  mocap_data


#--------------------------------------------------------------------------------
def getMarkers(data):

  marker_set_count = len(data.marker_set_data.marker_data_list)
  for i in range( 0, marker_set_count ):
    tmp=data.marker_set_data.marker_data_list[i].model_name.decode()
    if tmp.startswith('Building_'):
      print(tmp)
      marker_count = len(data.marker_set_data.marker_data_list[i].marker_pos_list)
      for j in range( 0, marker_count ):
        print(data.marker_set_data.marker_data_list[i].marker_pos_list[j])


#--------------------------------------------------------------------------------
def data_thread_function(in_socket, stop):
  message_id_dict={}
  data=bytearray(0)
  # 64k buffer size
  recv_buffer_size=64*1024

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
      if message_id == 7 : # NAT_FRAMEOFDATA :
        offset = 4
        mocap_data = unpack_mocap_data( data[offset:], packet_size )
#        mocap_data_str=mocap_data.get_as_string()
#        print("%s\n"%mocap_data_str)
        getMarkers(mocap_data)

        sys.exit(1)

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
