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

class ControlPanel(ConnectedObjects):
	# basic_mac = [id, mac_addr], basic_attrs = list of [attr name, sql type, python type]
	def __init__(self, facility, attrs, id, mac_addr):
		super(ControlPanel, self).__init__()

		self.facility = facility
		self.attrs = attrs
		
		# Initialize other object attributes as defined in attrs (see config file)
		for attr in attrs:
			name, mysql_type, py_type = attr
			if py_type == 'int':
				exec("self.%s = 0" % (name,))
			elif py_type == 'str':
				exec("self.%s = \"\"" % (name,))
			elif py_type == 'bool':
				exec("self.%s = False" % (name,))
			else:
				raise AttributeError("""Module initialized with at least one unknown 
										attribute type.""")

		self.id = int(id)
		self.mac_addr = mac_addr

	def setIP(self, ip):
		self.ip_addr = ip
		self.is_connected = 1
		self.life_points = self.facility.max_life_points

	def __del__(self):
		print "Control panel", self.id, "deleted."