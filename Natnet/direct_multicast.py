#!/usr/bin/python3
import socket
import struct
from threading import Thread

multicast="239.255.42.99"
dataPort=1511

#--------------------------------------------------------------------------------
def dataThreadFunction(sock):
  sock.settimeout(0.01)
  while True:
  # Block for input
   try:
     data, addr = sock.recvfrom( 32768 ) # 32k byte buffer size
     if( len( data ) >= 4):
       print( data )
   except socket.timeout:
     pass


def createDataSocket():
  result = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
  result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  result.bind( ('', dataPort))

  mreq = struct.pack("4sl", socket.inet_aton(multicast), socket.INADDR_ANY)
  result.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
  return result

#--------------------------------------------------------------------------------
if __name__ == '__main__':
  print("hello")
  dataSocket = createDataSocket()
  dataThread = Thread(target = dataThreadFunction, args = (dataSocket, ))
  dataThread.start()
