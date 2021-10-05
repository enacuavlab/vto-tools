#!/usr/bin/python3

import socket
import struct
from threading import Thread

DATAPORT=1511
COMMANDIP=('127.0.0.1',1510)
MULTICASTADDR='239.255.42.99'

NAT_PING                = 0
NAT_REQUEST             = 2
NAT_REQUEST_MODELDEF    = 4
NAT_REQUEST_FRAMEOFDATA = 6
NAT_FRAMEOFDATA         = 7

Vector3 = struct.Struct( '<fff' )
Quaternion = struct.Struct( '<ffff' )
FloatValue = struct.Struct( '<f' )


def createDataSocket( port ):
  result = socket.socket( socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
  result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  result.bind( ('', port) )
  mreq = struct.pack("4sl", socket.inet_aton(MULTICASTADDR), socket.INADDR_ANY)
  result.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
  return result

def createCommandSocket( ):
  result = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
  result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  result.bind( ('', 0) )
  result.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  return result

def receive_loop( sock ):
  sock.settimeout(0.01)
  while True:
    try:
      data, addr = sock.recvfrom( 32768 ) # 32k byte buffer size
      if( len( data ) >= 4): processMessage( data )
    except socket.timeout:
      pass

def processMessage( data ):
  messageID = int.from_bytes( data[0:2], byteorder='little' )
  print( "Message ID:", messageID )
  packetSize = int.from_bytes( data[2:4], byteorder='little' )
  print( "Packet Size:", packetSize )
  if not len( data ) - 4 >= packetSize: return
  offset = 4
  if( messageID == NAT_FRAMEOFDATA ): unpackMocapData( data[offset:] )


def unpackMocapData( data ):
  data = memoryview( data )
  offset = 0
  rigidBodyList = []
  frameNumber = int.from_bytes( data[offset:offset+4], byteorder='little' )
  offset += 4
  print( "Frame #:", frameNumber )
  markerSetCount = int.from_bytes( data[offset:offset+4], byteorder='little' )
  offset += 4
  print( "Marker Set Count:", markerSetCount )
  for i in range( 0, markerSetCount ):
    modelName, separator, remainder = bytes(data[offset:]).partition( b'\0' )
    offset += len( modelName ) + 1
    print( "Model Name:", modelName.decode( 'utf-8' ) )
    markerCount = int.from_bytes( data[offset:offset+4], byteorder='little' )
    offset += 4
    print( "Marker Count:", markerCount )
    for j in range( 0, markerCount ):
      pos = Vector3.unpack( data[offset:offset+12] )
      offset += 12
      print( "\tMarker", j, ":", pos[0],",", pos[1],",", pos[2] )

  unlabeledMarkersCount = int.from_bytes( data[offset:offset+4], byteorder='little' )
  offset += 4
  print( "Unlabeled Markers Count:", unlabeledMarkersCount )
  for i in range( 0, unlabeledMarkersCount ):
    pos = Vector3.unpack( data[offset:offset+12] )
    offset += 12
    print( "\tMarker", i, ":", pos[0],",", pos[1],",", pos[2] )

  rigidBodyCount = int.from_bytes( data[offset:offset+4], byteorder='little' )
  offset += 4
  print( "Rigid Body Count:", rigidBodyCount )
  for i in range( 0, rigidBodyCount ):
    offset += unpackRigidBody( data[offset:] )


def unpackRigidBody( data ):
  offset = 0
  id = int.from_bytes( data[offset:offset+4], byteorder='little' )
  offset += 4
  print("ID:", id )
  pos = Vector3.unpack( data[offset:offset+12] )
  offset += 12
  print( "\tPosition:", pos[0],",", pos[1],",", pos[2] )
  rot = Quaternion.unpack( data[offset:offset+16] )
  offset += 16
  print( "\tOrientation:", rot[0],",", rot[1],",", rot[2],",", rot[3] )
  markerError, = FloatValue.unpack( data[offset:offset+4] )
  offset += 4
  print( "\tMarker Error:", markerError )
  param, = struct.unpack( 'h', data[offset:offset+2] )
  trackingValid = ( param & 0x01 ) != 0
  offset += 2
  print( "\tTracking Valid:", 'True' if trackingValid else 'False' )
  return offset


def sendCommand( self, command, commandStr, socket, address ):
  if( command == NAT_REQUEST_MODELDEF or command == NAT_REQUEST_FRAMEOFDATA ):
    packetSize = 0
    commandStr = ""
  elif( command == NAT_REQUEST ):
    packetSize = len( commandStr ) + 1
  elif( command == NAT_PING ):
    commandStr = "Ping"
    packetSize = len( commandStr ) + 1
  data = command.to_bytes( 2, byteorder='little' )
  data += packetSize.to_bytes( 2, byteorder='little' )
  data += commandStr.encode( 'utf-8' )
  data += b'\0'
  socket.sendto( data, address )


if __name__ == '__main__':

  dataSocket = createDataSocket(DATAPORT)
  if( dataSocket is None ):
    print( "Could not open data channel" )
    exit
  commandSocket = createCommandSocket()
  if( commandSocket is None ):
    print( "Could not open command channel" )
    exit

  dataThread = Thread( target = receive_loop, args = (dataSocket, ))
  dataThread.start()

  commandThread = Thread( target = receive_loop, args = (commandSocket, ))
  commandThread.start()

  sendCommand( NAT_REQUEST_MODELDEF, "", commandSocket, COMMANDIP)
