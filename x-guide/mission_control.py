#!/usr/bin/env python

from __future__ import print_function

import sys
from os import path, getenv

# if PAPARAZZI_SRC or PAPARAZZI_HOME not set, then assume the tree containing this
# file is a reasonable substitute
PPRZ_HOME = getenv("PAPARAZZI_HOME", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
PPRZ_SRC = getenv("PAPARAZZI_SRC", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
sys.path.append(PPRZ_SRC + "/sw/lib/python")
sys.path.append(PPRZ_HOME + "/var/lib/python") # pprzlink

from pprzlink.ivy import IvyMessagesInterface
from pprzlink.message import PprzMessage
from settings_xml_parse import PaparazziACSettings

import pprz_connect
import settings
from vector_fields import TrajectoryEllipse, ParametricTrajectory, spheric_geo_fence, repel, Controller

from math import radians
import time
import numpy as np

class Commands():
    def __init__(self, ac_id, interface):
        self._ac_id = ac_id
        self._interface=interface

    def set_guided_mode(self, quad_id = None):
        """
        change mode to GUIDED.
        """
        if self.ap_mode is not None:
            msg = PprzMessage("ground", "DL_SETTING")
            msg['ac_id'] = self._ac_id
            msg['index'] = self.ap_mode.index
            try:
                msg['value'] = self.ap_mode.ValueFromName('Guided')  # AP_MODE_GUIDED
            except ValueError:
                try:
                    msg['value'] = self.ap_mode.ValueFromName('GUIDED')  # AP_MODE_GUIDED
                except ValueError:
                    msg['value'] = 19 # fallback to fixed index
            print("Setting mode to GUIDED: %s" % msg)
            self._interface.send(msg)

    def set_nav_mode(self):
        """
        change mode to NAV.
        """
        if self.ap_mode is not None:
            msg = PprzMessage("ground", "DL_SETTING")
            msg['ac_id'] = self._ac_id
            msg['index'] = self.ap_mode.index
            try:
                msg['value'] = self.ap_mode.ValueFromName('Nav')  # AP_MODE_NAV
            except ValueError:
                try:
                    msg['value'] = self.ap_mode.ValueFromName('NAV')  # AP_MODE_NAV
                except ValueError:
                    msg['value'] = 13 # fallback to fixed index
            print("Setting mode to NAV: %s" % msg)
            self._interface.send(msg)

    def takeoff(self):
        pass    

    def jump_to_block(self, block_id):
        """
        Jump to Flight Block 
        """
        msg = PprzMessage("ground", "JUMP_TO_BLOCK")
        msg['ac_id'] = self._ac_id
        msg['block_id'] = block_id
        print("jumping to block: %s" % block_id)
        print("ac id: %s" % self._ac_id)
        self._interface.send(msg)

    def land(self):
        pass

    def accelerate(self, north=0.0, east=0.0, down=0.0, flag=0):
        print('Accelerating')
        msg = PprzMessage("datalink", "DESIRED_SETPOINT")
        msg['ac_id'] = self._ac_id
        msg['flag'] = flag # 0:2D, 1:full 3D
        msg['ux'] = north
        msg['uy'] = east
        msg['uz'] = down
        self._interface.send(msg)


class FlightStatus(object):
    def __init__(self, ac_id):
        self._ac_id = ac_id
        self._state = None
        self._current_task = None
        self._current_task_key = None
        self._current_task_time = None
        self._current_task_duration = None
        self._current_task_last_time = 0.0
        self._mission_plan={}

    # @property
    def mission_plan(self):
        return self._mission_plan

    # @mission_plan.setter
    def set_mission_plan(self,m_p_dict):
        self._mission_plan = m_p_dict

    def check_current_task(self):
        # Assuming that the dictionaries will be always ordered... hmmm FIX_ME !!!
        # finalized_tasks =  [self._mission_plan[_k]['finalized'] for _k in self._mission_plan.keys()]
        # first_not_finalized_index = next((i for i, j in enumerate(finalized_tasks) if not j), None)
        # self._current_task = self._mission_plan.keys()[first_not_finalized_index]
        for _k in self._mission_plan.keys():
            if self._mission_plan[_k]['finalized'] == False:
                self._current_task = self._mission_plan[_k]
                self._current_task_key = _k
                self._current_task_duration = self._current_task['duration']
                if self._current_task['start'] != None : self._current_task_time = time.time()-self._current_task['start']
                break
        # Decide to finalize task according to its duration:
        if self._current_task['start'] == None :
            self._current_task['start'] = time.time()
        else:
            if time.time()-self._current_task['start'] > self._current_task_duration :
                self._mission_plan[self._current_task_key]['finalized'] = True


        # print(self._current_task_key)
        # return self._current_task
        #print(f'Mission Plan :{_k} is {self._mission_plan[_k]['start']}')
            
    @property
    def task(self):
        self.check_current_task()
        return self._current_task_key

    def get_current_task_time(self):
        self.check_current_task()
        return self._current_task_time


class Vehicle(object):
    def __init__(self, ac_id, interface):
        self._initialized = False
        self._take_off = False
        self._land = False
        self._ac_id = ac_id
        self._interface = interface
        self._position = np.zeros(3) # Position
        self._velocity = np.zeros(3) # Velocity
        self.W = np.zeros(3) # Angles
        self.gvf_parameter = 0
        self.sm = None  # settings manager
        self.timeout = 0
        self.cmd = Commands(self._ac_id, self._interface)
        self.fs = FlightStatus(self._ac_id)


        self.ka = 1.6 #acceleration setpoint coeff
        self.circle_vel = 0.6 #m/s
        self.belief_map = {}

    def __str__(self):
        conf_str = f'A/C ID {self._ac_id}'
        return conf_str

    @property
    def id(self):
        return self._ac_id

    @property
    def state(self):
        return self._state

    def assign_properties(self):
        # while self._initialized == False :
            print('Initialization :::',self._initialized)
            ex = 0 ; ey = 0 ; ealpha = 0 ; ea = 1.1 ; eb = 1.1
            print(f'We are inside assign properties for id {self._ac_id}')
            self.traj = TrajectoryEllipse(np.array([self._position[0], self._position[1]]), ealpha, ea, eb)
            self.ctr = Controller(L=1e-1,beta=1e-2,k1=1e-3,k2=1e-3,k3=1e-3,ktheta=0.5,s=1.0)
            self.traj_parametric = ParametricTrajectory(XYZ_off=np.array([0.,0.,2.5]),
                                                        XYZ_center=np.array([1.3, 1.3, -0.6]),
                                                        XYZ_delta=np.array([0., np.pi/2, 0.]),
                                                        XYZ_w=np.array([1,1,1]),
                                                        alpha=0.,
                                                        controller=self.ctr)

    def get_vector_field(self,mission_task):
        V_des = np.zeros(3)
        V_des += spheric_geo_fence(self._position[0], self._position[1], self._position[2], x_source=0., y_source=0., z_source=0., strength=-0.07)
        for _k in self.belief_map.keys():
            # float(self.belief_map[_k]['X'])
            V_des += repel(self._position[0], self._position[1], self._position[2], 
                    x_source=float(self.belief_map[_k]['X']), 
                    y_source=float(self.belief_map[_k]['Y']), 
                    z_source=float(self.belief_map[_k]['Z']), strength=4.0)

        return V_des

    def send_acceleration(self, V_des, A_3D=False):
        err = V_des - self._velocity#[:2]
        print(f'Velocity error {err[0]} , {err[1]}, {err[2]}')
        acc = err*self.ka
        if A_3D :
            self.cmd.accelerate(acc[0],acc[1],-acc[2], flag=1)
        else:
            self.cmd.accelerate(acc[0],acc[1],2, flag=0) # Z is fixed to have a constant altitude... FIXME for 3D !
        # return acc


    def calculate_cmd(self, mission_task):
        V_des = self.get_vector_field(self.fs.task)

        if mission_task == 'takeoff':
            print('TAKE-OFF!!!')
            if not self._take_off :
                self.cmd.jump_to_block(2)
                time.sleep(0.5)
                self.cmd.jump_to_block(2)
                self._take_off = True

        elif mission_task == 'circle':
            print('We are circling!!!')
            V_des += self.traj.get_vector_field(self._position[0], self._position[1], self._position[2])*self.circle_vel
            self.send_acceleration(V_des)

        elif mission_task == 'parametric_circle':
            print('We are circling with parametric circle !!!')
            # now = time.time() #self.fs.get_current_task_time()
            # dt = now-self.fs._current_task_last_time
            # self._current_task_last_time = now
            V_des_increment,uw = self.traj_parametric.get_vector_field(self._position[0], self._position[1], self._position[2], self.gvf_parameter)
            # import pdb
            # pdb.set_trace()
            # print(f'Shape of V_des : {V_des_increment.shape}')
            # print(f'dt : {0.1}, parameter : {self.gvf_parameter} ')
            V_des += V_des_increment 
            self.gvf_parameter += -uw[0]*0.1 #dt
            self.send_acceleration(V_des, A_3D=True)

        # print(self.belief_map.keys())
        elif mission_task == 'nav2land':
            print('We are going for landing!!!')
            self.send_acceleration(V_des) # This is 2D with fixed 2m altitude height AGL
            if self.fs._current_task_time > 3. : self.cmd.jump_to_block(5)


        elif mission_task == 'land':
            print('We are landing!!!')
            if not self._land :
                self.cmd.jump_to_block(5)
                self._land = True

        # else mission_task == 'kill' :


    def run(self):
        # while True:
        print(f'Running the vehicle {self._ac_id} in {self.fs.task} state ')
        self.calculate_cmd(self.fs.task)



# Callback for PprzConnect notify
def new_ac(conf):
    print(conf)


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
        time.sleep(0.5)
        # self.assign_vehicle_properties()

    def run_every_vehicle(self):
        # Once it is threaded, below lines can be used to start each vehicles runtime
        for _id in self._vehicle_id_list:
            rc = self.vehicles[self._vehicle_id_list.index(_id)]
            print(f'Vehicle id :{_id} and its index :{self._vehicle_id_list.index(_id)} Position {rc._position[1]}')
            self.update_belief_map(rc)
            rc.run()

    def assign(self,mission_plan_dict):
        i=0
        for _id in self._vehicle_id_list:
            print(f'Vehicle id :{_id} mission plan updated ! ')
            rc = self.vehicles[self._vehicle_id_list.index(_id)]
            rc.fs.set_mission_plan(mission_plan_dict)
            rc.gvf_parameter = (len(self._vehicle_id_list)-i)*20.
            i+=1

    def assign_vehicle_properties(self):
        for _id in self._vehicle_id_list:
            print('Here we are !!!!!!')
            rc = self.vehicles[self._vehicle_id_list.index(_id)]
            rc.assign_properties()

    def update_belief_map(self, vehicle):
        for _k in self._vehicle_position_map.keys():
            if _k != vehicle._ac_id:
                vehicle.belief_map[_k] = self._vehicle_position_map[_k]

    def update_vehicle_list(self):
        self._connect.get_aircrafts() # Not sure if we need that all the time, as it is subscribed for every NEW_AIRCRAFT...
        self.create_vehicles()

    def create_vehicles(self):
        self._vehicle_id_list=[int(_id) for _id in self._connect.conf_by_id().keys()]
        self.vehicles = [Vehicle(id, self._interface) for id in self._vehicle_id_list]

    def subscribe_to_msg(self):
        # bind to INS message
        def ins_cb(ac_id, msg):
            if ac_id in self.ids and msg.name == "INS":
                rc = self.rotorcrafts[self.ids.index(ac_id)]
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
                rc.W[2] = float(msg['psi']) * i2w
                self._vehicle_position_map[ac_id] = {'X':rc._position[0],'Y':rc._position[1],'Z':rc._position[2]}
                rc.timeout = 0
                rc._initialized = True
        
        # Un-comment this if the quadrotors are providing state information to use_deep_guidance.py
        #self._interface.subscribe(rotorcraft_fp_cb, PprzMessage("telemetry", "ROTORCRAFT_FP"))
    
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
                # print(f'Ground REF ac_id {ac_id}')
                # print(f'X:{rc._position[0]} Y: {rc._position[1]} Z: {rc._position[2]}')
                self._vehicle_position_map[ac_id] = {'X':rc._position[0],'Y':rc._position[1],'Z':rc._position[2]}
                rc.timeout = 0
                rc._initialized = True
        
        # Un-comment this if optitrack is being used for state information for use_deep_guidance.py **For use only in the Voliere**
        self._interface.subscribe(ground_ref_cb, PprzMessage("ground", "GROUND_REF"))
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
            print("Shutting down ivy interface...")
            self._interface.shutdown()
            self._interface = None

    def __del__(self):
        self.shutdown()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Mission Control")
    parser.add_argument("-ti", "--target_id", dest='target_id', default=2, type=int, help="Target aircraft ID")
    parser.add_argument("-ri", "--repel_id", dest='repel_id', default=2, type=int, help="Repellant aircraft ID")
    parser.add_argument("-bi", "--base_id", dest='base_id', default=10, type=int, help="Base aircraft ID")

    args = parser.parse_args()

    interface  = IvyMessagesInterface("PprzConnect")
    target_id = args.target_id

    mission_plan_dict={ 'takeoff' :{'start':None, 'duration':20, 'finalized':False},
                        'circle'  :{'start':None, 'duration':40, 'finalized':False},
                        'parametric_circle'  :{'start':None, 'duration':90, 'finalized':False},
                        'nav2land':{'start':None, 'duration':5,  'finalized':False},
                        'land'    :{'start':None, 'duration':10, 'finalized':False} } #,
                        # 'kill'    :{'start':None, 'duration':10, 'finalized':False} }
    
    # mission_plan_dict={ 'parametric_circle'  :{'start':None, 'duration':15, 'finalized':False} }

    vehicle_parameter_dict={}

    try:
        mc = MissionControl(interface=interface)
        mc.assign(mission_plan_dict)
        mc.assign_vehicle_properties()
        time.sleep(1.5)

        while True:
            mc.run_every_vehicle()
            time.sleep(0.1)



    except (KeyboardInterrupt, SystemExit):
        print('Shutting down...')
        # mc.set_nav_mode()
        mc.shutdown()
        time.sleep(0.6)
        exit()



if __name__ == '__main__':
    main()

#EOF
