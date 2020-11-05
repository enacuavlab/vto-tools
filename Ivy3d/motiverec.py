#!/usr/bin/env python3

import socket

SERVER="127.0.0.1"
CMD_PORT=1510
NAT_REQUEST = 2

class test:
  def __init__( self):
    self.cmdsocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    self.cmdsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.cmdsocket.bind( ('', 0) )
    self.cmdsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

  def sendCommand( self):
    command = NAT_REQUEST
    commandStr = "StartRecording"
    packetSize = len( commandStr ) + 1

    data = command.to_bytes( 2, byteorder='little' )
    data += packetSize.to_bytes( 2, byteorder='little' )
    data += commandStr.encode( 'utf-8' )
    data += b'\0'

    self.cmdsocket.sendto( data, (SERVER,CMD_PORT))

if __name__ == '__main__':
  srv=test()
  srv.sendCommand()
