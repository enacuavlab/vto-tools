#!/usr/bin/env python3

import sys
from os import path, getenv
from math import degrees, radians, sin, cos, atan2
import argparse
import socket

PPRZ_HOME = getenv("PAPARAZZI_HOME", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
PPRZ_SRC = getenv("PAPARAZZI_SRC", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
sys.path.append(PPRZ_SRC + "/sw/lib/python")
sys.path.append(PPRZ_HOME + "/var/lib/python") # pprzlink

from pprzlink.ivy import IvyMessagesInterface
from pprzlink.message import PprzMessage
import flight_plan
from pprz_connect import PprzConnect
import time
from enum import Enum

LAND_BLOCK = "flare"

class State(Enum):
    # FREE = 0
    GUIDED_FAR = 1
    GUIDED_CLOSE = 2
    LANDING = 3

class Guider:
    def __init__(self, ac_id, ivy):
        self.ac_id = ac_id
        self.ivy = ivy
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock.bind(("127.0.0.1",4000))
        self.sock.settimeout(0.5)
        
        self.msg = PprzMessage("datalink", "GUIDED_SETPOINT_NED")
        self.msg['ac_id'] = self.ac_id
        self.msg['flags'] = 0b1001010  # 0b1110
        self.flight_plan = None
        self.state = State.GUIDED_FAR
        self.ivy.subscribe(self.block_changed, PprzMessage("ground", "NAV_STATUS"))
        self.block = None
    
    def set_flight_plan(self, fp):
        self.flight_plan = flight_plan.FlightPlan.parse(fp)
        lh = self.flight_plan.get_block(LAND_BLOCK)
        print("Found block '{}' with no {}".format(lh.name, lh.no))
    
    def block_changed(self, sender, msg):
        if self.flight_plan is None:
            return
        cur_block = self.flight_plan.get_block(int(msg['cur_block']))
        if self.block != cur_block:
            print("block {}".format(cur_block.name))
            self.block = cur_block
        if cur_block.name == LAND_BLOCK:
            self.state = State.LANDING
    
    def run(self):
            while True:
                msg = self.msg
                try:
                    buf, addr = self.sock.recvfrom(1024)
                    a, b, c, d=(int(i) for i in buf.split())
                    yaw = radians(180 - d)
                    #print(yaw)
                    offset_x = -(b/1000)
                    offset_y = -(a/1000)
                    body_x =  offset_x * cos(yaw) + offset_y * sin(yaw)
                    body_y = -offset_x * sin(yaw) + offset_y * cos(yaw)

                    msg['x'] = body_x
                    msg['y'] = body_y

                    angle_wide = degrees(atan2(a, c))
                    angle_smal = degrees(atan2(b, c))
                    print(angle_wide, angle_smal)
                    
                    if c > 800:
                        self.state = State.GUIDED_FAR
                    else:
                        self.state = State.GUIDED_CLOSE

                    if abs(angle_wide) < 18 and abs(angle_smal) < 14:
                        # the drone is seen with some margins, lets descend.
                        factor = 5/max(abs(angle_wide), abs(angle_smal))
                        msg['z'] = min(0.2, 0.2 * factor)
                        # msg['z'] = 0.2
                    else:
                        # wait to be a bit more centered before going down.
                        msg['z'] = 0

                    #if c>=1000:d=c*0.4+300
                    #if 500<=c<=1000:d=c*0.6+100
                    #if c<=500:d=c*0.6

                    #msg['z']=round(d/1000,2)
                    msg['yaw'] = 0
                    print(msg)
                    self.ivy.send(msg)
                except(socket.timeout):
                    print("timeout aruco")
                    # aruco lost                    
                    if self.state == State.GUIDED_CLOSE:
                        lh = self.flight_plan.get_block(LAND_BLOCK)
                        print("Go to block {} no {}".format(lh.name, lh.no))
                        block_msg = PprzMessage("ground", "JUMP_TO_BLOCK")
                        block_msg['ac_id'] = self.ac_id
                        block_msg['block_id'] = lh.no
                        self.ivy.send(block_msg)
                    else:
                        # If the drone is still guided, stop it. Else, this message doesn't matter
                        msg['x'] = 0
                        msg['y'] = 0
                        msg['z'] = 0
                        msg['yaw'] = 0
                        self.ivy.send(msg)
                    
                    
                    
                except (KeyboardInterrupt, SystemExit):
                    print("Shutting down ivy ...")
                    self.ivy.shutdown()
                    exit(0)
                except OSError:
                    print("guided connection error")
                    self.ivy.stop()
                    exit(-1)
        
        

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
    
    
    pprz_connect = PprzConnect(ivy=ivy)
    
    guider = Guider(args.ac_id, ivy)
    while True:
        try:
            conf = pprz_connect.conf_by_id(str(args.ac_id))
            print(conf.flight_plan)
            guider.set_flight_plan(conf.flight_plan)
            break
        except KeyError:
            print("sleep...")
            time.sleep(0.1)
    
    guider.run()




