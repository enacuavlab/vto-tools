#!/usr/bin/env python3
from __future__ import print_function

import sys
import os
from os import path, getenv

from math import radians, atan2
import time
import numpy as np

# if PAPARAZZI_SRC or PAPARAZZI_HOME not set, then assume the tree containing this
# file is a reasonable substitute
PPRZ_HOME = getenv("PAPARAZZI_HOME", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
PPRZ_SRC = getenv("PAPARAZZI_SRC", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
sys.path.append(PPRZ_SRC + "/sw/lib/python")
sys.path.append(PPRZ_HOME + "/var/lib/python") # pprzlink
import settings
import pprz_connect
from settings_xml_parse import PaparazziACSettings

from pprzlink.ivy import IvyMessagesInterface

from pprzlink.message import PprzMessage

from vector_fields import TrajectoryEllipse, ParametricTrajectory, spheric_geo_fence, repel, Controller

import pdb

from scipy.spatial.transform import Rotation

from path_plan_w_panel import ArenaMap, Flow_Velocity_Calculation

from vehicle import Vehicle
# from commands import Commands

from components import Commands, FlightStatus





# Vehicle class was here...


# Callback for PprzConnect notify
def new_ac(conf):
    print(conf)

class SingleControl(object):
    def __init__(self, verbose=False, interface=None, quad_ids = None):
        self.verbose = verbose
        self._interface = interface
        # self._connect = pprz_connect.PprzConnect(notify=new_ac, ivy=self._interface, verbose=False)
        # if self._interface == None : self._interface = self._connect.ivy
        # time.sleep(0.5)
        # self._vehicle_id_list={}
        self._vehicle_position_map = {}
        self.update_vehicle_list()
        self.define_interface_callback()
        time.sleep(0.5)

    def define_interface_callback(self):

        def rotorcraft_fp_cb(ac_id, msg): # FIX ME : use single external function for this, instead of repeating...
            # print(self._vehicle_id_list)
            # ac_id = int(msg['ac_id'])
            # print(ac_id)
            if ac_id in self._vehicle_id_list and msg.name == "ROTORCRAFT_FP":
                rc = self.vehicles[self._vehicle_id_list.index(ac_id)]
                i2p = 1. / 2**8     # integer to position
                i2v = 1. / 2**19    # integer to velocity
                i2w = 1. / 2**12     # integer to angle
                rc._position[0] = float(msg['north']) * i2p
                rc._position[1] = float(msg['east']) * i2p
                rc._position[2] = float(msg['up']) * i2p
                rc._velocity[0] = float(msg['vnorth']) * i2v
                rc._velocity[1] = float(msg['veast']) * i2v
                rc._velocity[2] = float(msg['vup']) * i2v
                rc._euler[0] = float(msg['phi']) * i2w
                rc._euler[1] = float(msg['theta']) * i2w
                rc._euler[2] = float(msg['psi']) * i2w
                self._vehicle_position_map[ac_id] = {'X':rc._position[0],'Y':rc._position[1],'Z':rc._position[2]}
                rc.timeout = 0
                rc._initialized = True

        self._interface.callback = rotorcraft_fp_cb
        self._interface.start()

    def update_vehicle_list(self):
        self._vehicle_id_list=[42]#[int(_id) for _id in self._connect.conf_by_id().keys()]
        self.vehicles = [Vehicle(id, self._interface) for id in self._vehicle_id_list]
        # self.vehicle = Vehicle(42,self._interface)
        # self.create_vehicles()

    # def create_vehicles(self):
    #     self._vehicle_id_list=[int(_id) for _id in self._connect.conf_by_id().keys()]
    #     self.vehicles = [Vehicle(id, self._interface) for id in self._vehicle_id_list]

    def assign(self,mission_plan_dict):
        i=0
        for _id in self._vehicle_id_list:
            print(f'Vehicle id :{_id} mission plan updated ! ')
            rc = self.vehicles[self._vehicle_id_list.index(_id)]
            # rc.sm = settings.PprzSettingsManager(self._connect.conf_by_id(str(rc.id)).settings, str(rc.id), self._connect.ivy)
            rc.fs.set_mission_plan(mission_plan_dict)
            rc.gvf_parameter = (len(self._vehicle_id_list)-i)*30.
            i+=1
    
    def assign_vehicle_properties(self):
        for _id in self._vehicle_id_list:
            rc = self.vehicles[self._vehicle_id_list.index(_id)]
            rc.assign_properties()
               
    def update_belief_map(self, vehicle):
        for _k in self._vehicle_position_map.keys():
            if _k != vehicle._ac_id:
                vehicle.belief_map[_k] = self._vehicle_position_map[_k]

    def run_vehicle(self):
        for _id in self._vehicle_id_list:
            rc = self.vehicles[self._vehicle_id_list.index(_id)]
            self.update_belief_map(rc)
            rc.run()

    def shutdown(self):
        if self._interface is not None:
            print("Shutting down THE interface...")
            self._interface.shutdown()
            self._interface = None

    def __del__(self):
        self.shutdown()

class MissionControl(object):
    def __init__(self, verbose=False, interface=None, quad_ids = None):
        self.verbose = verbose
        self._interface = interface
        self._connect = pprz_connect.PprzConnect(notify=new_ac, ivy=self._interface, verbose=False)
        if self._interface == None : self._interface = self._connect.ivy
        time.sleep(0.5)
        # self._vehicle_id_list={}
        self._vehicle_position_map = {}
        self.update_vehicle_list()  # self.create_vehicles()
        self.subscribe_to_msg()
        self.flow_vels = np.zeros([len(self.vehicles),3])
        time.sleep(0.5)
        # self.assign_vehicle_properties()

    def run_every_vehicle(self, velocity_limit=0.6, flight_height=20., method='None'):
        self.calculate_Arena_Flow()
        # Once it is threaded, below lines can be used to start each vehicles runtime
        for _id in self._vehicle_id_list:
            _index = self._vehicle_id_list.index(_id)
            rc = self.vehicles[_index]
            rc.Set_Flight_Height(flight_height)
            V_des = self.flow_vels[_index].copy()
            V_des_mag = np.linalg.norm(V_des)
            V_des_unit = V_des/V_des_mag
            mag_clipped = np.clip(V_des_mag, 0., velocity_limit)
            rc.Set_Desired_Velocity(V_des_unit*mag_clipped, method=method) # direct - projection
            # print(f'Vehicle id :{_id} and its index :{self._vehicle_id_list.index(_id)} Position {rc._position[1]}')
            self.update_belief_map(rc)
            rc.run()

    def assign(self,mission_plan_dict):
        i=0
        for _id in self._vehicle_id_list:
            print(f'Vehicle id :{_id} mission plan updated ! ')
            rc = self.vehicles[self._vehicle_id_list.index(_id)]
            rc.sm = settings.PprzSettingsManager(self._connect.conf_by_id(str(rc.id)).settings, str(rc.id), self._connect.ivy)
            rc.fs.set_mission_plan(mission_plan_dict)
            rc.gvf_parameter = (len(self._vehicle_id_list)-i)*30.
            i+=1

    def assign_vehicle_properties(self):
        for _id in self._vehicle_id_list:
            rc = self.vehicles[self._vehicle_id_list.index(_id)]
            rc.assign_properties()

    def update_belief_map(self, vehicle):
        for _k in self._vehicle_position_map.keys():
            if _k != vehicle._ac_id:
                vehicle.belief_map[_k] = self._vehicle_position_map[_k]

    def update_vehicle_list(self):
        self._connect.get_aircrafts() # Not sure if we need that all the time, as it is subscribed for every NEW_AIRCRAFT...
        self.create_vehicles()

    def create_Arena(self, arena_version=102, radius = 0.3, panel_size=0.01, force_init=False):
        Arena_not_created = True
        if not force_init:
            # if this file exists.... FIX ME
            self.Arena = np.load(os.path.dirname(os.path.abspath(__file__))+"/matrix/arena_version"+str(arena_version)+".npy", 'rb')
            Arena_not_created = False

        if Arena_not_created:
            self.Arena = ArenaMap(version = arena_version)
            self.Arena.Inflate(radius = radius)
            self.Arena.Panelize(size=panel_size)
            self.Arena.Calculate_Coef_Matrix()
            # Saving arena for the next time :
            print('Saving the calculated Arena Matrix...')
            with open(os.path.dirname(os.path.abspath(__file__))+"/matrix/arena_version"+str(arena_version)+".npy", 'wb') as arena_file:
                np.savez(arena_file)


    def calculate_Arena_Flow(self):
        self.flow_vels = Flow_Velocity_Calculation(self.vehicles,self.Arena)
        rot = np.array([[0.,  1.,  0.],
                        [1.,  0.,  0.],
                        [0.,  0.,  1.]])
        self.flow_vels = rot.dot(self.flow_vels.T).T


    def assign_path_plan_properties(self, vehicle_id_list, vehicle_source_list, vehicle_imaginary_source_list, vehicle_goal_list, vehicle_goto_goal_list, vehicle_next_goal_list):
        for _id,set_source,set_imaginary_source,set_goal,set_goto_goal, next_goal_list in zip(vehicle_id_list, vehicle_source_list, vehicle_imaginary_source_list, vehicle_goal_list, vehicle_goto_goal_list, vehicle_next_goal_list):
            rc = self.vehicles[self._vehicle_id_list.index(_id)]
            rc.Set_Source(set_source)
            rc.Set_Imaginary_Source(set_imaginary_source)
            rc.Set_Goal(set_goal[0],set_goal[1],set_goal[2])
            rc.Go_to_Goal(set_goto_goal[0],set_goto_goal[1],set_goto_goal[2],set_goto_goal[3])
            rc.Set_Next_Goal_List(next_goal_list)

    def create_vehicles(self):
        self._vehicle_id_list=[int(_id) for _id in self._connect.conf_by_id().keys()]
        self.vehicles = [Vehicle(id, self._interface) for id in self._vehicle_id_list]

    def subscribe_to_msg(self):
        # bind to ENERGY message
        def energy_cb(ac_id, msg):
            if ac_id in self._vehicle_id_list and msg.name == "ENERGY":
                rc = self.vehicles[self._vehicle_id_list.index(ac_id)]
                rc.battery_voltage = float(msg['voltage'])

        self._interface.subscribe(energy_cb, PprzMessage("telemetry", "ENERGY"))

        # bind to INS message
        def ins_cb(ac_id, msg):
            # if ac_id in self.ids and msg.name == "INS":
            #     rc = self.rotorcrafts[self.ids.index(ac_id)]
            if ac_id in self._vehicle_id_list and msg.name == "INS":
                rc = self.vehicles[self._vehicle_id_list.index(ac_id)]
                i2p = 1. / 2**8     # integer to position
                i2v = 1. / 2**19    # integer to velocity
                rc._position[0] = float(msg['ins_x']) * i2p
                rc._position[1] = float(msg['ins_y']) * i2p
                rc._position[2] = float(msg['ins_z']) * i2p
                rc._velocity[0] = float(msg['ins_xd']) * i2v
                rc._velocity[1] = float(msg['ins_yd']) * i2v
                rc._velocity[2] = float(msg['ins_zd']) * i2v
                rc.timeout = 0
                rc._initialized = True
        # self._interface.subscribe(ins_cb, PprzMessage("telemetry", "INS"))

        #################################################################
        def rotorcraft_fp_cb(ac_id, msg):
            # print(self._vehicle_id_list)
            # ac_id = int(msg['ac_id'])
            # print(ac_id)
            if ac_id in self._vehicle_id_list and msg.name == "ROTORCRAFT_FP":
                rc = self.vehicles[self._vehicle_id_list.index(ac_id)]
                i2p = 1. / 2**8     # integer to position
                i2v = 1. / 2**19    # integer to velocity
                i2w = 1. / 2**12     # integer to angle
                rc._position[0] = float(msg['north']) * i2p
                rc._position[1] = float(msg['east']) * i2p
                rc._position[2] = float(msg['up']) * i2p
                rc._velocity[0] = float(msg['vnorth']) * i2v
                rc._velocity[1] = float(msg['veast']) * i2v
                rc._velocity[2] = float(msg['vup']) * i2v

                rc._position_enu[1] = float(msg['north']) * i2p
                rc._position_enu[0] = float(msg['east']) * i2p
                rc._position_enu[2] = float(msg['up']) * i2p
                rc._velocity_enu[1] = float(msg['vnorth']) * i2v
                rc._velocity_enu[0] = float(msg['veast']) * i2v
                rc._velocity_enu[2] = float(msg['vup']) * i2v

                rc._euler[0] = float(msg['phi']) * i2w
                rc._euler[1] = float(msg['theta']) * i2w
                rc._euler[2] = float(msg['psi']) * i2w
                self._vehicle_position_map[ac_id] = {'X':rc._position[0],'Y':rc._position[1],'Z':rc._position[2]}
                rc.timeout = 0
                rc._initialized = True
        
        # Un-comment this if the quadrotors are providing state information to use_deep_guidance.py
        self._interface.subscribe(rotorcraft_fp_cb, PprzMessage("telemetry", "ROTORCRAFT_FP"))
    


        def fixed_wing_xy_cb(ac_id, msg):
            # print('Callback : ', ac_id, msg.name)
            # ac_id = int(msg['ac_id'])
            if ac_id in self._vehicle_id_list and msg.name == "NAVIGATION":
                fw = self.vehicles[self._vehicle_id_list.index(ac_id)]
                fw._position[0] = float(msg['pos_x'])
                fw._position[1] = float(msg['pos_y'])

                fw._position_enu[0] = float(msg['pos_x'])
                fw._position_enu[1] = float(msg['pos_y'])

        def fixed_wing_z_cb(ac_id, msg):
            # ac_id = int(msg['ac_id'])
            if ac_id in self._vehicle_id_list:
                fw = self.vehicles[self._vehicle_id_list.index(ac_id)]
                fw._position[2] = float(msg['alt'])/1000.
                fw._position_enu[2] = float(msg['alt'])/1000.
                fw._course = float(msg['course'])*np.pi/1800.
                fw._speed = float(msg['speed'])/100.
                # Calculate Velocity
                fw._velocity = np.array([np.cos(fw._course)*fw._speed, np.sin(fw._course)*fw._speed, float(msg['climb'])*100.])

        self._interface.subscribe(fixed_wing_xy_cb, PprzMessage("telemetry", "NAVIGATION"))
        self._interface.subscribe(fixed_wing_z_cb, PprzMessage("telemetry", "GPS"))




        # bind to GROUND_REF message : ENAC Voliere is sending LTP_ENU
        def ground_ref_cb(ground_id, msg):
            ac_id = int(msg['ac_id'])
            if ac_id in self._vehicle_id_list:
                rc = self.vehicles[self._vehicle_id_list.index(ac_id)]
                # X and V in NED
                rc._position[0] = float(msg['pos'][1])
                rc._position[1] = float(msg['pos'][0])
                rc._position[2] = float(msg['pos'][2])
                rc._velocity[0] = float(msg['speed'][1])
                rc._velocity[1] = float(msg['speed'][0])
                rc._velocity[2] = float(msg['speed'][2])
                # Also in ENU
                rc._position_enu[0] = float(msg['pos'][0])
                rc._position_enu[1] = float(msg['pos'][1])
                rc._position_enu[2] = float(msg['pos'][2])
                rc._velocity_enu[0] = float(msg['speed'][0])
                rc._velocity_enu[1] = float(msg['speed'][1])
                rc._velocity_enu[2] = float(msg['speed'][2])
                # Unitary quaternion representing LTP to BODY orientation (qi, qx, qy, qz)
                rc._quat[0] = float(msg['quat'][0])
                rc._quat[1] = float(msg['quat'][2])
                rc._quat[2] = float(msg['quat'][1])
                rc._quat[3] = -float(msg['quat'][3])

                rc._euler = quat2euler(rc._quat)

                rc._w[0] = float(msg['rate'][0])
                rc._w[1] = float(msg['rate'][1])
                rc._w[2] = float(msg['rate'][2])
                # pdb.set_trace()
                # print(f'Ground REF ac_id {ac_id}')
                # print(f'X:{rc._position[0]} Y: {rc._position[1]} Z: {rc._position[2]}')
                self._vehicle_position_map[ac_id] = {'X':rc._position[0],'Y':rc._position[1],'Z':rc._position[2]}
                rc.timeout = 0
                rc._initialized = True
        
        # Un-comment this if optitrack is being used for state information for use_deep_guidance.py **For use only in the Voliere**
        # self._interface.subscribe(ground_ref_cb, PprzMessage("ground", "GROUND_REF"))

        ################################################################

    # <message name="ROTORCRAFT_FP" id="147">
    #   <field name="east"     type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
    #   <field name="north"    type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
    #   <field name="up"       type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
    #   <field name="veast"    type="int32" alt_unit="m/s" alt_unit_coef="0.0000019"/>
    #   <field name="vnorth"   type="int32" alt_unit="m/s" alt_unit_coef="0.0000019"/>
    #   <field name="vup"      type="int32" alt_unit="m/s" alt_unit_coef="0.0000019"/>
    #   <field name="phi"      type="int32" alt_unit="deg" alt_unit_coef="0.0139882"/>
    #   <field name="theta"    type="int32" alt_unit="deg" alt_unit_coef="0.0139882"/>
    #   <field name="psi"      type="int32" alt_unit="deg" alt_unit_coef="0.0139882"/>
    #   <field name="carrot_east"   type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
    #   <field name="carrot_north"  type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
    #   <field name="carrot_up"     type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
    #   <field name="carrot_psi"    type="int32" alt_unit="deg" alt_unit_coef="0.0139882"/>
    #   <field name="thrust"        type="int32"/>
    #   <field name="flight_time"   type="uint16" unit="s"/>
    # </message>

    # <message name="INS" id="198">
    #   <field name="ins_x"     type="int32" alt_unit="m"    alt_unit_coef="0.0039063"/>
    #   <field name="ins_y"     type="int32" alt_unit="m"    alt_unit_coef="0.0039063"/>
    #   <field name="ins_z"     type="int32" alt_unit="m"    alt_unit_coef="0.0039063"/>
    #   <field name="ins_xd"    type="int32" alt_unit="m/s"  alt_unit_coef="0.0000019"/>
    #   <field name="ins_yd"    type="int32" alt_unit="m/s"  alt_unit_coef="0.0000019"/>
    #   <field name="ins_zd"    type="int32" alt_unit="m/s"  alt_unit_coef="0.0000019"/>
    #   <field name="ins_xdd"   type="int32" alt_unit="m/s2" alt_unit_coef="0.0009766"/>
    #   <field name="ins_ydd"   type="int32" alt_unit="m/s2" alt_unit_coef="0.0009766"/>
    #   <field name="ins_zdd"   type="int32" alt_unit="m/s2" alt_unit_coef="0.0009766"/>
    # </message>

    def shutdown(self):
        if self._interface is not None:
            print("Shutting down THE interface...")
            self._interface.shutdown()
            self._interface = None

    def __del__(self):
        self.shutdown()

# def rotorcraft_fp_cb(ac_id, msg):
#             # print(self._vehicle_id_list)
#             # ac_id = int(msg['ac_id'])
#             print('BAAM ', ac_id)
#             if ac_id in self._vehicle_id_list and msg.name == "ROTORCRAFT_FP":
#                 rc = self.vehicles[self._vehicle_id_list.index(ac_id)]
#                 i2p = 1. / 2**8     # integer to position
#                 i2v = 1. / 2**19    # integer to velocity
#                 i2w = 1. / 2**12     # integer to angle
#                 rc._position[0] = float(msg['north']) * i2p
#                 rc._position[1] = float(msg['east']) * i2p
#                 rc._position[2] = float(msg['up']) * i2p
#                 rc._velocity[0] = float(msg['vnorth']) * i2v
#                 rc._velocity[1] = float(msg['veast']) * i2v
#                 rc._velocity[2] = float(msg['vup']) * i2v
#                 rc._euler[2] = float(msg['psi']) * i2w
#                 self._vehicle_position_map[ac_id] = {'X':rc._position[0],'Y':rc._position[1],'Z':rc._position[2]}
#                 rc.timeout = 0
#                 rc._initialized = True

def quat2euler(quat):
    '''quat : Unitary quaternion representing LTP to BODY orientation (qi, qx, qy, qz) '''
    # from scipy.spatial.transform import Rotation
    _quat=np.array([quat[1], quat[2], quat[3], quat[0] ])
    rot = Rotation.from_quat(_quat)
    # rot_euler = rot.as_euler('yxz', degrees=False)
    rot_euler = rot.as_euler('xyz', degrees=False)
    return rot_euler


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Mission Control")
    parser.add_argument("-on", "--running-on", help="Where is the code running-on", dest='running_on', default='ground')
    parser.add_argument("-f", "--file", help="path to messages.xml file", default='pprzlink/messages.xml')
    parser.add_argument("-c", "--class", help="message class", dest='msg_class', default='telemetry')
    parser.add_argument("-d", "--device", help="device name", dest='dev', default='/dev/ttyUSB0') #ttyTHS1
    parser.add_argument("-b", "--baudrate", help="baudrate", dest='baud', default=230400, type=int)
    parser.add_argument("-id", "--ac_id", help="aircraft id (receiver)", dest='ac_id', default=42, type=int)
    parser.add_argument("--interface_id", help="interface id (sender)", dest='id', default=0, type=int)
    # parser.add_argument("-ti", "--target_id", dest='target_id', default=2, type=int, help="Target aircraft ID")
    # parser.add_argument("-ri", "--repel_id", dest='repel_id', default=2, type=int, help="Repellant aircraft ID")
    # parser.add_argument("-bi", "--base_id", dest='base_id', default=10, type=int, help="Base aircraft ID")
    args = parser.parse_args()

    if args.running_on == 'ground' :
        interface  = IvyMessagesInterface("PprzConnect")

    if args.running_on == "serial" :
        from pprzlink.serial import SerialMessagesInterface
        interface = SerialMessagesInterface(None, device=args.dev,
                                               baudrate=args.baud, msg_class=args.msg_class, interface_id=args.id, verbose=False)


    mission_plan_dict={# 'takeoff' :{'start':None, 'duration':20, 'finalized':False},
                        # 'circle'  :{'start':None, 'duration':15, 'finalized':False},
                        'parametric_circle'  :{'start':None, 'duration':15, 'finalized':False},
                        # 'nav2land':{'start':None, 'duration':5,  'finalized':False},
                        # 'land'    :{'start':None, 'duration':10, 'finalized':False} } #,
                        # 'kill'    :{'start':None, 'duration':10, 'finalized':False} }
                        }
    # mission_plan_dict={ 'parametric_circle'  :{'start':None, 'duration':15, 'finalized':False} }

    vehicle_parameter_dict={}

    if args.running_on == 'ground' :
        try:
            mc = MissionControl(interface=interface)
            mc.assign(mission_plan_dict)
            mc.assign_vehicle_properties()
            time.sleep(1.5)

            while True:
                mc.run_every_vehicle()
                time.sleep(0.09)

        except (KeyboardInterrupt, SystemExit):
            mission_end_plan_dict={'safe2land'  :{'start':None, 'duration':15, 'finalized':False}, }
            mc.assign(mission_end_plan_dict)  # mc.assign_vehicle_properties()
            time.sleep(0.5)
            for i in range(10):
                mc.run_every_vehicle()
                time.sleep(0.5)
            print('Shutting down...')
            # mc.set_nav_mode()
            mc.shutdown()
            time.sleep(0.6)
            exit()

    if args.running_on == 'serial' :
        try:
            sc = SingleControl(interface=interface)
            sc.assign(mission_plan_dict)
            sc.assign_vehicle_properties()
            time.sleep(1.5)

            while True:
                sc.run_vehicle()
                time.sleep(0.09)

        except (KeyboardInterrupt, SystemExit):
            mission_end_plan_dict={'safe2land'  :{'start':None, 'duration':15, 'finalized':False}, }
            sc.assign(mission_end_plan_dict) # sc.assign_vehicle_properties()
            time.sleep(0.5)
            for i in range(10):
                sc.run_vehicle()
                time.sleep(0.5)
            print('Shutting down...')
            # mc.set_nav_mode()
            sc.shutdown()
            time.sleep(0.6)
            exit()


if __name__ == '__main__':
    main()

#EOF
