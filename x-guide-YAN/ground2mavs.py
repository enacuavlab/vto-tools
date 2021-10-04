#!/usr/bin/python3

import sys
from os import path, getenv

PPRZ_HOME = getenv("PAPARAZZI_HOME", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
PPRZ_SRC = getenv("PAPARAZZI_SRC", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
sys.path.append(PPRZ_SRC + "/sw/lib/python")
sys.path.append(PPRZ_HOME + "/var/lib/python") # pprzlink

from pprzlink.ivy import IvyMessagesInterface
from pprzlink.message import PprzMessage

import pprz_connect
import socket
import struct
import time
import numpy as np

GROUND2MAVSPORT=4300
#/home/pprz/Projects/compagnon-software/wifibroadcast/wfb_tx -K /home/pprz/Projects/compagnon-software/wifibroadcast/gs.key -p 7 -u 4300 -k 1 -n 2 wlx3c7c3fa9bfbb
#/home/pprz/Projects/compagnon-software/wifibroadcast/wfb_rx -K /home/pprz/Projects/compagnon-software/wifibroadcast/gs.key -p 7 -u 4300 -c 127.0.0.1 -k 1 -n 2 wlx3c7c3fa9bfbb

GROUND2MAVS=1

STX = 0x99

global sock,addr_out

def new_ac(conf):
    print(conf)

def calculate_checksum(msg):
  ck_a = 0
  ck_b = 0
  for c in msg[1:]:
    if isinstance(c, str): c = struct.unpack("<B", c)[0]
    ck_a = (ck_a + c) % 256
    ck_b = (ck_b + ck_a) % 256
  return ck_a, ck_b


def ground_ref_cb(ground_id, msg):

  acid = int(msg['ac_id'])
#  if ac_id in self._vehicle_id_list:
  if acid == 51:
    position=np.zeros(3);velocity=np.zeros(3)
    position[0] = float(msg['pos'][0])
    position[1] = float(msg['pos'][1])
    position[2] = float(msg['pos'][2])
    velocity[0] = float(msg['speed'][0])
    velocity[1] = float(msg['speed'][1])
    velocity[2] = float(msg['speed'][2])
    payload  = struct.pack('B',acid)
    payload += struct.pack('ffffff',position[0],position[1],position[2],velocity[0],velocity[1],velocity[2])
    msg = struct.pack("BBBBBB", STX, 33, 0, 0, 0, GROUND2MAVS) + payload
    (ck_a, ck_b) = calculate_checksum(msg)
    msg += struct.pack('BB', ck_a, ck_b)
    global sock,addr_out
    sock.sendto(msg, addr_out)


if __name__ == '__main__':

  try:
    global sock,addrout
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr_out = ('localhost', GROUND2MAVSPORT)

  except OSError:
    print("Error: unable to open socket on ports")
    exit(0)

  ivy = IvyMessagesInterface("ground2mavs")
  ivy.subscribe(ground_ref_cb, PprzMessage("ground", "GROUND_REF"))
