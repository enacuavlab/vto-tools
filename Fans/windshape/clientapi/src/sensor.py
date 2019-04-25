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
from connectedObjects import ConnectedObjects

class Sensor(ConnectedObjects):
	""" Sensor instances are usually created from the constructor of Facility. 
	The attributes of Sensor are created from the reading of a configuration file. """
	def __init__(self, facility, attrs, sens_id, name, mac_addr):
		super(Sensor, self).__init__()
		
		self.facility = facility
		self.attrs = attrs
		
		# Initialize other object attributes as defined in attrs (see config file)
		for attr in attrs:
			nom, mysql_type, py_type = attr
			if py_type == 'int':
				exec("self.%s = 0" % (nom,))
			elif py_type == 'str':
				exec("self.%s = \"\"" % (nom,))
			elif py_type == 'bool':
				exec("self.%s = False" % (nom,))
			else:
				raise AttributeError("""Module initialized with at least one unknown 
										attribute type.""")
		
		self.id = int(sens_id)
		self.name = name
		self.mac_addr = mac_addr

		self.format_msg_client_to_server = [("id", "int"),
									("cmd_send_data", "bool"),
									("cmd_sample_rate", "int"),
									("cmd_reboot", "bool"),]

		self.format_msg_server_to_client = [("id", "int"),
									("pos_x", "int"),
									("pos_y", "int"),
									("pos_z", "int"),
									("state_send_data", "bool"),
									("state_sample_rate", "int"),
									("data1", "text"),
									("data2", "text"),
									("life_points", "int"),
									("is_connected", "bool")]

	def setIP(self, ip):
		self.ip_addr = ip
		self.is_connected = 1
		self.life_points = self.facility.max_life_points

	def __del__(self):
		print "Sensor", self.id, "deleted."
