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

from fan import Fan
from math import sqrt

class FanUnit(object):
	""" FanUnit is normally initiated form the constructior of Module. 
	FanUnit comprises a list "fans" which contains at least one Fan object. If more 
	than one Fan is stored in the list "fans" it means that the FanUnit is composed by 
	multiple Fan in series. """
	def __init__(self, module, fan_id):
		self.module = module
		self.fan_id = fan_id

		# Position (x, y) in meter. This is set in the initialization of FanWall.
		self.coords = (0, 0)

		self.fans = []
		for i in range(self.module.fan_layers):
			self.fans.append(Fan(self))

		self.isSelected = False

	def getPosInModule(self):
		""" return (x, y) position of the fan in the module. Both x and y start
		at 0. """
		nfan_x = sqrt(self.module.fan_number)
		nfan_y = nfan_x
		return (self.fan_id%nfan_x, (self.fan_id/nfan_x)%nfan_y)

	def setPWM(self, pwm):
		""" Sets a given PWM value for all Fans of the FanUnit. """
		for fan in self.fans:
			fan.pwm = pwm

	def setPWMs(self, pwms):
		""" Sets PWM values for all Fans of the FanUnit, given rpms, a list of int. """
		for i, fan in enumerate(self.fans):
			fan.pwm = pwms[i]

	def getPWMs(self, server_status=False):
		""" Return pwms, a list of pwm, based on the fans pwm of the fan unit."""
		pwms = []
		for fan in self.fans:
			pwms.append(fan.getPWM(server_status))
		return pwms

	def getPWM_mean(self, server_status=False):
		""" Return the mean PWM value of all Fan of the FanUnit. Used only for
		graphical representation of the FanUnit (i.e. colorscale that represents
		the PWM command). """
		pwms = [fan.getPWM(server_status) for fan in self.fans]	
		return int(round(sum(pwms)/len(pwms)))

	def setRPMs(self, rpms):
		""" Sets RPM values for all Fans of the FanUnit, given rpms, a list of int. """
		for i, fan in enumerate(self.fans):
			fan.rpm = rpms[i]

	def getRPMs(self):
		""" Return RPMs, a list of RPM, based on the RPM of each fan of the fan unit."""
		rpms = []
		for fan in self.fans:
			rpms.append(fan.getRPM())
		return rpms

	def getRPM_mean(self):
		""" Return the mean RPM value of all Fan of the FanUnit. Used only for
		graphical representation of the FanUnit (i.e. colorscale that represents
		the RPM command). """
		rpms = [fan.getRPM() for fan in self.fans]	
		return int(round(sum(rpms)/len(rpms)))


