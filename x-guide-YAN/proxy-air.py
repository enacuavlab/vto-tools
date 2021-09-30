#!/usr/bin/python3

import socket
import select
import struct
import threading
import signal
import time

import sys
import serial

from proxy_common import *


class ethernet2serial(threading.Thread):
  def __init__(self, fd):
    threading.Thread.__init__(self)
    self.fd = fd
    self.shutdown_flag = threading.Event()
    self.running = True
    self.streams = {}
    self.addr_out = ('localhost', BOARDCLI)
    for port in [DATALINK,BOARDSERV]:
       sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       sock.bind(('localhost', port))
       self.streams[sock] = (port,PprzTransport())

  def stop(self):
    for s in self.sockets: s.close()
    self.running = False
    self.server.close()


  def run(self):
    try:
      sockets = self.streams.keys()
      while self.running  and not self.shutdown_flag.is_set():
        try:
          (readable, writable, exceptional) = select.select(sockets, [], [])
          for s in readable:
            (data, address) = s.recvfrom(1024)
            port,transport = self.streams[s]
            for c in data:
              if not isinstance(c, bytes): c = struct.pack("B",c)
              if transport.parse_byte(c):
                self.fd.write(transport.buf)
                # STX + length + sender_id + receiver + comp/class + msg_id + data + ck_a + ck_b
                (start,length,sender,receiver,comp,msgid) = struct.unpack('BBBBBB',transport.buf[0:6])
                #if  ((msgid == REMOTE_GPS_LOCAL) and (comp == 0x02)): s.sendto(transport.buf,self.addr_out)
                if ((msgid == SETTING) and (comp == 0x02)): s.sendto(transport.buf,self.addr_out)
        except socket.timeout:
          pass
    except StopIteration:
      pass



#SERIAL='/dev/ttyUSB0'
SERIAL='/dev/ttyAMA0'
BAUDRATE=115200

if __name__ == '__main__':

  ser = serial.Serial(SERIAL, BAUDRATE)

  streams = []
  streams.append(ethernet2serial(ser))


  for thread in streams: thread.start()
  try:
    while True:
      time.sleep(2)
  except KeyboardInterrupt:
    for thread in streams:
      thread.shutdown_flag.set()
      thread.join()
