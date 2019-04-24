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

class ConnectedObjects(object):
	def __init__(self):
		pass
		
	def decayLifePoints(self):
		self.life_points -= 1
		if self.life_points <= 0:
			self.life_points = 0
			self.is_connected = 0
			self.ip_addr = ''

	def getAttributeValue(self, attr_name):
		""" Given a name (str) of attribute, return its value.
		@TODO add failsafe in case this method is called by not module with "pwm" or "rpm" arguments """

		# Retreive the type to be returned
		for attr in self.attrs:
			name, mysql_type, py_type = attr
			if name == attr_name:
				attr_type = py_type

		if attr_name == "rpm":
			value = self.getRPMstr()
		elif attr_name == "pwm":
			value = self.getPWMstr()
		else:
			exec("value = self.%s" % (attr_name,))

		if attr_type:
			if attr_type == 'int':
				value = int(value)
			elif attr_type == 'bool':
				value = int(value)
			elif attr_type == 'str':
				value = str(value)
			else:
				raise TypeError("Error type not defined.")
		else:
			raise TypeError("Can't read type from modules attr list.")

		return value

	def setAttributeValue(self, attr_name, attr_value, attr_type):
		""" Given an attribute name (str), its value, and its type (str) this method 
		properly sets the attibute value. """

		if attr_name == "pwm":
			self.setPWMstr(attr_value)
		elif attr_name == "rpm":
			self.setRPMstr(attr_value)
		elif attr_type == 'int':
			exec("self.%s = int(%d)" % (attr_name, int(attr_value)))
		elif attr_type == 'str':
			exec("self.%s = str(%s)" % (attr_name, attr_value))
		elif attr_type == 'bool':
			exec("self.%s = int(%s)" % (attr_name, attr_value))

	def getMsg(self, dest):
		""" Called by modules and sensors to generate message to send, wheter to server or to client"""
		if dest == "server":
			msg_format = self.format_msg_client_to_server
		elif dest == "client":
			msg_format = self.format_msg_server_to_client
		else:
			facility.addToPrintBuff("[ERROR] Invalid dest in method getMsg().")
			return ""

		msg = ""
		for attr in msg_format:
			attr_name = attr[0]
			if attr_name == "pmw":
				msg += getPWMstr()
				msg += ";"
			else:
				add = str(self.getAttributeValue(attr_name))
				if add == "True":
					msg += "1"
				elif add == "False":
					msg += "0"
				else:
					msg += add

				msg += ";"

		return msg[:-1]


