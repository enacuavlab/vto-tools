#!/usr/bin/env python3

import socket
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(("127.0.0.1", 9090))

while True:

  data, addr = sock.recvfrom(1024)

  floats = list(struct.unpack('>3d',data))
  print(floats)
