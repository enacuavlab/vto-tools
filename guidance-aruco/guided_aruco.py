#!/usr/bin/env python3

import sys
from os import path, getenv

import argparse
import socket

PPRZ_HOME = getenv("PAPARAZZI_HOME", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
PPRZ_SRC = getenv("PAPARAZZI_SRC", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
sys.path.append(PPRZ_SRC + "/sw/lib/python")
sys.path.append(PPRZ_HOME + "/var/lib/python") # pprzlink

from pprzlink.ivy import IvyMessagesInterface
from pprzlink.message import PprzMessage

def clamp(n, minn, maxn):
  if n < minn:return 0
  elif n > maxn:return maxn-minn
  else:return n-minn

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Guided mode example")
  parser.add_argument("-i", "--ac_id", dest='ac_id', type=int, required=True)
  parser.add_argument('-b', '--ivy_bus', dest='ivy_bus')
  args = parser.parse_args()

  if args.ivy_bus is not None:
    ivy = IvyMessagesInterface("guided", ivy_bus=args.ivy_bus)
  else:
    ivy = IvyMessagesInterface("guided")

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  sock.bind(("127.0.0.1",4000))

  msg = PprzMessage("datalink", "GUIDED_SETPOINT_NED")
  msg['ac_id'] = args.ac_id
  msg['flags'] = 0x0E

  try:
    while True:
      buf, addr = sock.recvfrom(1024)
      a,b=(int(x) for x in buf.split())
      msg['x']:=clamp(a,83,563)  # [0,480]
      msg['y']=clamp(b,171,363) # [0,192]
      msg['z'] = 0
      msg['yaw'] = 0
      ivy.send(msg)
  except (KeyboardInterrupt, SystemExit):
    print("Shutting down ivy ...")
    ivy.shutdown()
  except OSError:
    print("guided connection error")
    ivy.stop()
    exit(-1)
