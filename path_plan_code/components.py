import sys
from os import path, getenv

import numpy as np
import time

PPRZ_HOME = getenv("PAPARAZZI_HOME", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
PPRZ_SRC = getenv("PAPARAZZI_SRC", path.normpath(path.join(path.dirname(path.abspath(__file__)), '../../../../')))
sys.path.append(PPRZ_SRC + "/sw/lib/python")
sys.path.append(PPRZ_HOME + "/var/lib/python") # pprzlink
import settings
import pprz_connect
from settings_xml_parse import PaparazziACSettings

from pprzlink.ivy import IvyMessagesInterface

from pprzlink.message import PprzMessage


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
        # print('Accelerating')
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

class Circle():
    def __init__(self, radius=1.5, cx=0.0, cy=0.0, cz=4.0):
        self.radius = radius
        self.cx = cx
        self.cy = cy
        self.cz = cz