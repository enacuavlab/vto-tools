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
    
class Fan(object):
	def __init__(self, fan_unit):
		self.fan_unit = fan_unit
		self.pwm = 0
		self._pwm_server_status = 0
		self.rpm = 0
		
	def setPWM(self, pwm, server_status=False):
		if server_status:
			self._pwm_server_status = pwm
		else:
			self.pwm = pwm

	def getPWM(self, server_status=False):
		if server_status:
			return self._pwm_server_status
		return self.pwm

	def setRPM(self, rpm):
		self.rpm = rpm

	def getRPM(self):
		return self.rpm

