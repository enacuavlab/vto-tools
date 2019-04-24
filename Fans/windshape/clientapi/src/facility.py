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

from fanWall import FanWall
from sensor import Sensor
from controlPanel import ControlPanel
from client import Client
import utilities as ut
import time

class Facility(object):
	def __init__(self, conf_path):
		self.conf_path = conf_path
		self.frequency = int(ut.readConfig(self.conf_path, "FREQ", 0)[0][0])
		
		self.ports = map(int, ut.readConfig(self.conf_path, "PORTS", 0)[0])
		self.db_access = ut.readConfig(self.conf_path, "DEFINE_DB", 0)[0]
		self.max_life_points = int(ut.readConfig(self.conf_path, "MAX_LIFE_POINTS", 0)[0][0])
		self.config_address = ut.readConfig(self.conf_path, "CONFIG_ADDRESS", 0)[0][0]

		self.stop_flag = 0

		self.fan_walls = self.createFanWalls()
		self.sensors, self.sensor_attrs, self.sensor_macs = self.createSensors()
		self.control_panel, self.control_panel_attrs, self.control_panel_mac = self.createControlPanel()

		self.configuration = {}

		self.verbose = int(ut.readConfig(self.conf_path, "VERBOSE", 0)[0][0])
		self.module_verbose = int(ut.readConfig(self.conf_path, "MODULE_VERBOSE", 0)[0][0])

		# Rolling buffer for printing
		self.print_buff_size = 100
		self.print_buff = ['']*self.print_buff_size # print buffer
		self.print_i = 0 # buffer iterator
		self.i_old = 0

		# Position of "client" in list "clients" is equal to "client_id"
		self.clients = [] # List of command clients (webapp, or any other sending on ports[5])

		self.control_token = 'free' # can be "free", "emergency", "control_panel" or client_ip

		self.client_in_charge_name = '' # Usefull only for client side

		# On server, updated by interpretMsgStatus. On client, updated by API or GUI.
		self.cmd_logging = False

		# On server, updated by logging thread, sent to client via getMsgStatus. On client, updated by interpretMsgStatus.
		self.state_logging = False

		# @TODO REMOVE THE FOLLOWING
		# Array that contains the posistions x and y of the fans in the array. The origin is at the 
		# bottom left fan and the axis are pointing up and right. Each point of the grid is at 
		# the center of an existing fan of the array.
		#self.fan_coords_array = self.getFanCoordsArray()

	
	def getMsgStatus(self, dest, client):
		''' This method is used both by the client and by the server !
		It return a status string to send to 'dest'.'''
		msg_status = "STATUS@" + str(client.id) + ":"
		
		if dest == "client":
			# Is client in charge
			is_in_charge = 0
			if str(self.control_token) == str(client.id):
				is_in_charge = 1
			msg_status += str(is_in_charge) + ";"

			# ID of client in charge, or free, or emergency, or control_panel
			msg_status += str(self.control_token) + ";"

			# Name of client in charge (navigator or API)
			name_in_charge = ""
			for client in self.clients:
				if str(client.id) == str(self.control_token):
					name_in_charge = client.name
					break

			msg_status += name_in_charge + ";"

			# Connection status of the control_panel
			if self.control_panel:
				msg_status += str(self.control_panel.is_connected) + ";"
			else:
				msg_status += "0;"

			# Is the server program logging
			msg_status += str(int(self.state_logging)) + "\0"

			return msg_status

		elif dest == "server":
			 # The client calling this method has to be the first (or only) client listed in the factiliy !!!!!
			
			msg_status += str(self.clients[0].token_request) + ";"
			msg_status += str(int(self.cmd_logging)) + "\0"
			return msg_status

		else:
			self.addToPrintBuff("[MESSAGE] Wrong dest input ! (not server or client)")
			return ""

	def getMsgModule(self, dest, client):
		""" Depending on the consignee (dest), this method returns a strings 
		that contains all the attributes from modules that have to be sent to "dest". """
		msg_mod = "MODULE@"+str(client.id)+":"
		for fan_wall in self.fan_walls:
			for module in fan_wall.modules_flat:
				msg_mod += module.getMsg(dest)
				msg_mod += "|"

		msg_mod = msg_mod[:-1] + "\0"

		return msg_mod

	def getMsgSensor(self, dest, client):
		""" Depending on the consignee (dest), this method returns a strings 
		that contains all the attributes from sensorsthat have to be sent to "dest". """
		msg_sens = "SENSOR@"+str(client.id)+":"
		for sensor in self.sensors:
			msg_sens += sensor.getMsg(dest)
			msg_sens = msg_sens + "|"

		msg_sens = msg_sens[:-1] + "\0"

		return msg_sens

	def interpretMsgModule(self, msg, dest):
		""" When the server or client receives a message, it has to interpret it. 
		This method is used to de-compile the message and to propagate the commands from the
		client to the server's modules objects. """

		# Remove  end-of-line char if any
		if "\0" in msg:
			msg, _ = msg.split("\0", 1)

		if ":" in msg:
			msg_header, msg_content = msg.split(":", 1)
		else:
			msg_content = msg

		mod_msgs = msg_content.split("|")
		for mod_msg in mod_msgs:
			attr_values = mod_msg.split(";")
			mod_id = attr_values[0]
			
			# Retrieve the module to who the part of the message is addressed
			current_module = None
			for fan_wall in self.fan_walls:
				for module in fan_wall.modules_flat:
					if int(module.id) == int(mod_id):
						current_module = module
						break

			# Set the module's attributes that where reveived
			for i, attr_value in enumerate(attr_values):
				if dest == "server":
					attr_name = current_module.format_msg_client_to_server[i][0]
					attr_type = current_module.format_msg_client_to_server[i][1]
									# Do not override the module ID
					if attr_name == "id":
						continue

					current_module.setAttributeValue(attr_name, attr_value, attr_type)

				elif dest == "client":
					attr_name = current_module.format_msg_server_to_client[i][0]
					attr_type = current_module.format_msg_server_to_client[i][1]

					# @WARNING !!!  HEAVY MODIFICATION HERE
					# (see Module.init_attibutes_from_server_dict())
					if attr_type == 'str':
						current_module.attibutes_from_server_dict[attr_name] = str(attr_value)
					elif attr_type == 'int':
						current_module.attibutes_from_server_dict[attr_name] = int(attr_value)
					elif attr_type == 'bool':
						current_module.attibutes_from_server_dict[attr_name] = int(attr_value)

			if dest == 'client':
				current_module.writeServerStatus()
					# ---------------------------------------------------------

	def interpretMsgSensor(self, msg, dest):
		""" When the server or the client receives a message, it has to interpret it. 
		This method is used to de-compile the message and to propagate the commands from the
		client to the sensor's objects. """

		# Remove  end-of-line char if any
		if "\0" in msg:
			msg, _ = msg.split("\0", 1)

		if ":" in msg:
			msg_header, msg_content = msg.split(":", 1)
		else:
			msg_content = msg

		sens_msgs = msg_content.split("|")
		for sens_msg in sens_msgs:
			attr_values = sens_msg.split(";")
			sens_id = attr_values[0]
			
			# Retrieve the module to who the part of the message is addressed
			current_sensor = None
			for sensor in self.sensors:
				if int(sensor.id) == int(sens_id):
					current_sensor = sensor
					break

			# Set the module's attributes that where reveived
			for i, attr_value in enumerate(attr_values):
				if dest == "server":
					attr_name = current_sensor.format_msg_client_to_server[i][0]
					attr_type = current_sensor.format_msg_client_to_server[i][1]

				elif dest == "client":
					attr_name = current_module.format_msg_server_to_client[i][0]
					attr_type = current_module.format_msg_server_to_client[i][1]

				if attr_name == "id":
					continue
				current_module.setAttributeValue(attr_name, attr_value, attr_type)

	def interpretMsgStatus(self, msg, dest, client=None):
		""" When the server or the client receives a message, it has to interpret it. 
		This method is used to de-compile the message and to propagate the commands from the
		client to the objects. """
		
		# @REMOVE
		# if ":" in msg:
		# 	msg_header, msg_content = msg.split(":", 1)
		# else:
		# 	msg_content = msg
		
		if "\0" in msg:
			msg, _ = msg.split("\0", 1)
		
		attr_values = msg.split(";")

		if dest == "server":
			# @REMOVE
			# Find which client is sending data
			# current_client = None
			# for client in self.clients:
			# 	if client.ip_addr == client_ip:
			# 		current_client = client
			# 		break

			# Set token
			if client:
				client.token_request = int(attr_values[0])
			self.cmd_logging = int(attr_values[1])

		elif dest == "client":
			self.clients[0].in_charge = attr_values[0]
			self.control_token = attr_values[1]
			self.client_in_charge_name = attr_values[2]
			self.state_logging = int(attr_values[3])
			if self.control_panel:
				self.control_panel.is_connected = attr_values[4]
			

	def updateControlToken(self):
		''' Called by client receiving thread, this method updates the control token and turns off the fans if the control panel or a client is lost.'''
		if self.control_token == "emergency":
			# The token is set and released to "emergency" by any client at any moment.
			return

		if self.control_panel:
			
			if self.control_panel.is_connected and self.control_panel.token_request:
				self.control_token = "control_panel"
				return
			
			elif (not self.control_panel.is_connected or not self.control_panel.token_request) and self.control_token == 'control_panel':
				self.control_token = "free"
				self.control_panel.token_request = 0
				self.turnOffFans()
				self.turnOffPSUs()

		elif self.control_token == "control_panel":
			self.control_token = "free"

		if self.control_token != "control_panel":
			if self.control_token != "free":
				incharge_client = None
				for client in self.clients:
					if client.id == self.control_token:
						incharge_client = client
						break

				if incharge_client == None:
					self.control_token = "free"
					self.turnOffFans()

				elif incharge_client.is_connected and incharge_client.token_request:
					return

				elif not incharge_client.is_connected or (incharge_client.is_connected and not incharge_client.token_request):
					self.control_token = "free"
					self.turnOffFans()

			#if control_token == "free"
			else:
				for client in self.clients:
					if client.token_request == 1 or client.token_request == "1":
						self.control_token = client.id						
						break

	def turnOffFans(self):
		'''Stop all fans in case of lost connection with control panel'''
		for fan_wall in self.fan_walls:
			for module in fan_wall.modules_flat:
				module.setPWM(0)

	def turnOffPSUs(self):
		'''Stop all PSUs in case of lost connection with control panel'''
		for fan_wall in self.fan_walls:
			for module in fan_wall.modules_flat:
				module.set_cmd_powered(0)
				module.set_cmd_send_rpm(0)

	def createFanWalls(self):

		str_fan_walls = ut.readConfig(self.conf_path, "FAN_WALLS", 0)

		fan_walls = []
		for str_fan_wall in str_fan_walls:
			fan_walls.append(FanWall(self, str_fan_wall, self.conf_path))

		return fan_walls

	def createSensors(self):

		attrs = ut.readConfig(self.conf_path, "DEFINE_SENSORS", 1)
		macs = ut.readConfig(self.conf_path, "SENSORS_MAC", 0)

		attrs = ut.formatAttrs(attrs)

		sensors = []
		for mac in macs:
			sensors.append(Sensor(self, attrs, mac[0], mac[1], mac[2]))
		
		return sensors, attrs, macs

	def createControlPanel(self):
		
		# List of list n x (atrs, mysqltype, python type)
		attrs = ut.readConfig(self.conf_path, "DEFINE_CONTROL_PANEL", 1) 

		attrs = ut.formatAttrs(attrs)

		# List of [macAddr, ipAddr] for each control panel 
		macs = ut.readConfig(self.conf_path, "CONTROL_PANEL_MAC", 0)

		if len(macs) > 0:
			mac = macs[0]
		else: 
			mac = []

		if len(mac) == 2:
			control_panel = ControlPanel(self, attrs, mac[0], mac[1])
		else:
			control_panel = None

		return control_panel, attrs, mac

	def createClient(self, client_ip, client_id, client_name):
		''' Create a new client and adds it in list'''
		self.clients.append(Client(self, client_ip, client_id, client_name))

	def removeClient(self, ip_addr):
		for i, client in enumerate(self.clients):
			if client.ip_addr == ip_addr:
				del self.clients[i]

	def addToPrintBuff(self, text_to_print):
			if self.verbose == 1:
				self.print_buff[self.print_i] = text_to_print
				self.print_i = (self.print_i+1)%self.print_buff_size

	def printBuffer(self):
		if self.print_i == self.i_old:
			pass
		else:
			print self.print_buff[self.i_old]
			time.sleep(0.01)
			self.i_old = (self.i_old+1)%self.print_buff_size

	def __del__(self):
		print "Facility deleted."



