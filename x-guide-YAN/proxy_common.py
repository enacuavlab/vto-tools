#!/usr/bin/python3

import struct

DATALINK=4245
BOARDSERV=4310
BOARDCLI=4320

def calculate_checksum(msg):
  ck_a = 0
  ck_b = 0
  for c in msg[1:]:
    if isinstance(c, str): c = struct.unpack("<B", c)[0]
    ck_a = (ck_a + c) % 256
    ck_b = (ck_b + ck_a) % 256
  return ck_a, ck_b

# PPRZLINK V2.0
# STX , LENGTH, SENDER, DESTINATION, CLASS, ID, PAYLOAD, CHCKA, CHCKB
try:
    from enum import Enum
except ImportError:
    Enum = object

STX = 0x99

SETTING=4
DESIRED_SETPOINT=15
REMOTE_GPS_LOCAL=56

class PprzParserState(Enum):
    WaitSTX = 1
    GotSTX = 2
    GotLength = 3
    GotPayload = 4
    GotCRC1 = 5

class PprzTransport(object):
    def __init__(self):
        self.state = PprzParserState.WaitSTX
        self.length = 0
        self.buf = []
        self.ck_a = 0
        self.ck_b = 0
        self.idx = 0

    def parse_byte(self, c):
        b = struct.unpack("<B", c)[0]
        if self.state == PprzParserState.WaitSTX:
            if b == STX:
                self.state = PprzParserState.GotSTX
        elif self.state == PprzParserState.GotSTX:
            self.length = b - 4
            if self.length <= 0:
                self.state = PprzParserState.WaitSTX
                return False
            self.buf = bytearray(b)
            self.ck_a = b % 256
            self.ck_a = b % 256
            self.ck_b = b % 256
            self.buf[0] = STX
            self.buf[1] = b
            self.idx = 2
            self.state = PprzParserState.GotLength
        elif self.state == PprzParserState.GotLength:
            self.buf[self.idx] = b
            self.ck_a = (self.ck_a + b) % 256
            self.ck_b = (self.ck_b + self.ck_a) % 256
            self.idx += 1
            if self.idx == self.length+2:
                self.state = PprzParserState.GotPayload
        elif self.state == PprzParserState.GotPayload:
            if self.ck_a == b:
                self.buf[self.idx] = b
                self.idx += 1
                self.state = PprzParserState.GotCRC1
            else:
                self.state = PprzParserState.WaitSTX
        elif self.state == PprzParserState.GotCRC1:
            self.state = PprzParserState.WaitSTX
            if self.ck_b == b:
                self.buf[self.idx] = b
                return True
        else:
            self.state = PprzParserState.WaitSTX
        return False
