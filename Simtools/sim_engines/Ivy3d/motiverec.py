#!/usr/bin/env python3

import socket
import time

SERVER="192.168.1.231"
CMD_PORT=1510

def init_request():
  cmdsocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
  cmdsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  cmdsocket.bind( ('', 0) )
  cmdsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  return(cmdsocket)

def send_request(sock,commandStr):
  packetSize = len( commandStr ) + 1
  command = 2 # NAT_REQUEST
  data = command.to_bytes( 2, byteorder='little' )
  data += packetSize.to_bytes( 2, byteorder='little' )
  data += commandStr.encode( 'utf-8' )
  data += b'\n'
  sock.sendto( data, (SERVER,CMD_PORT))

sock=init_request()
send_request(sock,"StartRecording")
time.sleep(5)
send_request(sock,"StopRecording")
