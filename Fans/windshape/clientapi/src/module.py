"""
Copyright (C) WindShape LLC - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential. 
                     _ _ _ _       _ _____ _               
                    | | | |_|___ _| |   __| |_ ___ ___ ___  
                    | | | | |   | . |__   |   | .'| . | -_| 
                    |_____|_|_|_|___|_____|_|_|__,|  _|___| 
                                                  |_|        
 
WindShape LLC, Geneva, February 2019 

Developer team:
	Guillaume Catry <guillaume.catry@windshape.ch>
	Nicolas Bosson <nicolas.bosson@windshape.ch>

Contributors:
	Adrien Fleury, Alejandro Stefan Zavala, Federico Conzelmann
"""

from math import sqrt
from fanUnit import FanUnit
from connectedObjects import ConnectedObjects
import time

class Module(ConnectedObjects):
	""" Module instances are usually created from the constructor of FanWall. 
	The attributes of Module are created from the reading of a configuration 
	file. """
	def __init__(self, fan_wall, attrs, mod_id, mac_addr, pos_x, pos_y, 
				 fan_number, fan_layers):
		super(Module, self).__init__()	

		self.fan_wall = fan_wall
		self.attrs = attrs

		# Initialize other object attributes as defined in attrs 
		# (see config file)
		for attr in attrs:
			name, mysql_type, py_type = attr
			if py_type == 'int':
				exec("self.%s = 0" % (name,))
			elif py_type == 'str':
				exec("self.%s = \"\"" % (name,))
			elif py_type == 'bool':
				exec("self.%s = False" % (name,))
			else:
				raise AttributeError("""Module initialized with at least 
										one unknown attribute type.""")

		# Deleted to avoid confusion. PWM and RPM are attribute of fans and not modules !
		# However, pwm and rpm need to be present in attrs for database creation.
		del self.pwm
		del self.rpm

		self.id = int(mod_id)
		self.mac_addr = mac_addr
		self.pos_x = int(pos_x)
		self.pos_y = int(pos_y)
		self.fan_number = int(fan_number)
		self.fan_layers = int(fan_layers)

		# Instantiate FanUnits and store in both a 2D list "self.fan_units" 
		# and a flat list "self.fan_units_flat"
		a = int(sqrt(self.fan_number))
		self.fan_units = [[FanUnit(self, i+j) for i in range(a)] for j in range(a)] 
		self.fan_units_flat = [item for sublist in self.fan_units for item in sublist]
		self.fans_flat = []
		for fan_unit in self.fan_units_flat:
			for fan in fan_unit.fans:
				self.fans_flat.append(fan)

		self.format_msg_client_to_server = [("id", "int"),
											("pwm", "str"),
											("cmd_powered", "bool"),
											("cmd_send_rpm", "bool"),
											("cmd_flashing", "bool"),
											("cmd_reboot", "bool")]

		self.format_msg_server_to_client = [("id", "int"),
											("pwm", "str"),
											("rpm", "str"),
											("cmd_powered", "bool"),
											("state_powered", "bool"),
											("cmd_send_rpm", "bool"),
											("state_send_rpm", "bool"),
											("cmd_flashing", "bool"),
											("state_flashing", "bool"),
											("life_points", "int"),
											("is_connected", "bool")]

		self.attibutes_from_server_dict = {}

		self.init_attibutes_from_server_dict()

	def init_attibutes_from_server_dict(self):
		""" WORKAROUND !!!
		These attributes are used to store attributes sent by the server on the client side.
		The problem was, on the client side if we dont store the module attributes recvd from 
		server in separate variables then... whathever, I'll remeber it... ask Guillaume Catry.
		""" 
		for attr in self.format_msg_server_to_client:
			attr_name, attr_type = attr
			if attr_type == 'int':
				self.attibutes_from_server_dict[attr_name] = 0
			elif attr_type == 'str':
				self.attibutes_from_server_dict[attr_name] = ""
			elif attr_type == 'bool':
				self.attibutes_from_server_dict[attr_name] = False
			else:
				raise AttributeError("""initServerStatusAttributes() initialized with at least 
										one unknown attribute type.""")

	def writeServerStatus(self):
		""" Called from Facility.interpretMsgModule(). Propagate pwm and rpm str into fan units and
		fans.  """
		self.setPWMstr(self.attibutes_from_server_dict['pwm'], server_status=True)
		self.setRPMstr(self.attibutes_from_server_dict['rpm'])

	def setPWM(self, pwm):
		""" Set the PWM value of all fans of the module to a single value and update 
		self.pwm. """
		for fan_unit in self.fan_units_flat:
			fan_unit.setPWM(pwm)

	def setPWMs(self, pwms):
		""" Set the PWM value of all fans of the module to a single value and update 
		self.pwm. """
		for fan_unit in self.fan_units_flat:
			fan_unit.setPWMs(pwms)

	def setRPMs(self, rpms):
		""" Set the PWM value of all fans of the module to correct values. """
		for fan_unit in self.fan_units_flat:
			fan_unit.setRPMs(rpms)

	def getPWMstr(self):
		""" Concatenate the PWM values from all fans of the module into a string 
		return it. """ 
		pwm_str = ""
		for fan_unit in self.fan_units_flat:
			for fan in fan_unit.fans:
				pwm_str += str(fan.getPWM(server_status=False))+","
		pwm_str = pwm_str[:-1]
		return pwm_str

	def setPWMstr(self, pwm_str, server_status=False):
		""" Given a list of coma separated PWM (str), sets properly the PWM values of
		all fans of the module. """

		pwms = pwm_str.split(",")

		# Check if len(pwms) == len(self.fans_flat). fans_flat contains all fans (not fan_units)
		if len(pwms) == len(self.fans_flat):
			for i, fan in enumerate(self.fans_flat):
				fan.setPWM(int(pwms[i]), server_status)
		else:
			time.sleep(1)
			raise ValueError("in Module.setPWMstr(pwm_str), len(pwms) != len(Module.fans_flat)")

	def getRPMstr(self):
		""" Get and concatenate the value of RPM from all fans into a string and
		returns it. """ 
		rpm_str = ""
		for fan_unit in self.fan_units_flat:
			for fan in fan_unit.fans:
				rpm_str += str(fan.rpm)+","
		rpm_str = rpm_str[:-1]
		return rpm_str

	def setRPMstr(self, rpm_str):
		""" Given a list of coma separated RPM (str), sets properly the RPM values of
		all fans of the module. """
		
		rpms = rpm_str.split(",")

		# Check if len(pwms) == len(self.fans_flat). fans_flat contains all fans (not fan_units)
		if len(rpms) == len(self.fans_flat):
			for i, fan in enumerate(self.fans_flat):
				fan.setRPM(int(rpms[i]))
		else:
			raise ValueError("in Module.setRPMstr(rpm_str), len(rpms) != len(Module.fans_flat)")

	def setIP(self, ip):
		self.ip_addr = ip
		self.is_connected = 1
		self.life_points = self.fan_wall.facility.max_life_points

	def set_cmd_powered(self, cmd):
		self.cmd_powered = int(cmd)

	def set_cmd_send_rpm(self, cmd):
		self.cmd_send_rpm = int(cmd)

	def set_cmd_flashing(self, cmd):
		self.cmd_flashing = int(cmd)

	def set_cmd_reboot(self, cmd):
		self.cmd_reboot = int(cmd)

	def get_cmd_flashing(self, server_status=False):
		if server_status:
			return self.attibutes_from_server_dict["cmd_flashing"]
		return self.cmd_flashing

	def get_cmd_send_rpm(self, server_status=False):
		if server_status:
			return self.attibutes_from_server_dict["cmd_send_rpm"]
		return self.cmd_send_rpm

	def get_cmd_powered(self, server_status=False):
		if server_status:
			return self.attibutes_from_server_dict["cmd_powered"]
		return self.cmd_powered

	def get_state_send_rpm(self, server_status=False):
		if server_status:
			return self.attibutes_from_server_dict["state_send_rpm"]
		return self.state_send_rpm

	def get_state_powered(self, server_status=False):
		if server_status:
			return self.attibutes_from_server_dict["state_powered"]
		return self.state_powered

	def get_state_flashing(self, server_status=False):
		if server_status:
			return self.attibutes_from_server_dict["state_flashing"]
		return self.state_flashing

	def get_life_points(self, server_status=False):
		if server_status:
			return self.attibutes_from_server_dict["life_points"]
		return self.life_points

	def get_is_connected(self, server_status=False):
		if server_status:
			return self.attibutes_from_server_dict["is_connected"]
		return self.is_connected

	def __del__(self):
		print "Module", self.id, "deleted."