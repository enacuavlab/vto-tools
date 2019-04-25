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

from module import Module
import utilities as ut

class FanWall(object):
	def __init__(self, facility, name, conf_path):
		self.conf_path = conf_path
		self.facility = facility
		self.name = name

		# Is it easily doable without creating "fan_layout" ?
		self.fan_layout = ut.readConfig(self.conf_path, "DEFINE_FANS", 0)
		self.fan_number = int(self.fan_layout[0][0])
		self.fan_layers = int(self.fan_layout[0][1])

		# Flat list of Module objects, module_attrs is useful to be able to get the attributes even if no module is created
		self.modules_flat, self.module_attrs, self.module_macs = self.createModules()

		# 2D list of Module objects 
		nxs = [mod.pos_x for mod in self.modules_flat]
		nys = [mod.pos_y for mod in self.modules_flat]
		nx = max(nxs)-1
		ny = max(nys)-1

		self.modules = [[self.modules_flat[i+j*(nx+1)] for i in range(nx+1)] for j in range(ny+1)]


		self.modules_dict = self.createModulesDict()


		# 2D list that store FanUnits
		self.fan_units = self.arrangeFansInList2D()

		# Flat list that stores the Fan units
		self.fan_units_flat = [item for sublist in self.fan_units for item in sublist]

		# Set fan_units coordinate in meter - FanUnit.coords = (x, y) 
		self.setFansCoordinates()

	def arrangeFansInList2D(self):
		""" Return a 2D list of all fans comprised in the FanWall. """
		fans = []
		new_fans_line = []
		for module_line in self.modules:
			for fan_line in range(3):
				for module in module_line:
					for fan_col in range(3):
						fan = module.fan_units[fan_line][fan_col]
						new_fans_line.append(fan)
				fans.append(new_fans_line)
				new_fans_line = []
		return fans

	def createModules(self):
		attrs = ut.readConfig(self.conf_path, "DEFINE_MODULES", 1)
		macs = ut.readConfig(self.conf_path, "MODULES_MAC", 0)

		attrs = ut.formatAttrs(attrs)

		modules = []
		for mac in macs:
			id, pos_y, pos_x, mac_addr  = mac
			new_module = Module(self, attrs, id, mac_addr, pos_x, pos_y, self.fan_number, self.fan_layers)
			modules.append(new_module)

		return modules, attrs, macs

	def createModulesDict(self):
		""" Return a dictionnary that associate module.id with module:
			mod_dict = {module.id: module} """
		mod_dict = {}
		for module in self.modules_flat:
			mod_dict[module.id] = module
		return mod_dict

	def getModuleByID(self, id):
		""" Return the unique module with the given ID (int). """
		return self.modules_dict[int(id)]

	# def getFanCoordsArray(self):
	# 	""" Return the X-Y positions of the fans of the array. """
	# 	n_fan_x = len(self.fan_units[0])
	# 	n_fan_y = len(self.fan_units)
	# 	coords_array = [[(0.08*ix, 0.08*iy) for ix in range(n_fan_x)] for iy in reversed(range(n_fan_y))]
	# 	return coords_array

	def setFansCoordinates(self):
		n_fan_x = len(self.fan_units[0])
		n_fan_y = len(self.fan_units)
		for iy, fan_units_line in enumerate(self.fan_units):
			for ix, fan_unit in enumerate(fan_units_line):
				coords = (0.08*ix, 0.08*(n_fan_y-iy))
				fan_unit.coords = coords

	def get_state_send_rpm(self, server_status=False):
		""" Return 0 if property is unset for all modules, 1 if sets for some but 
		not all modules, 2 if set for all modules. """
		state = 0
		count = 0
		for module in self.modules_flat:
			if int(module.get_state_send_rpm(server_status)):
				state = 1
				count += 1
		if count == len(self.modules_flat):
			state = 2
		return state

	def get_state_powered(self, server_status=False):
		""" Return 0 if property is unset for all modules, 1 if sets for some but 
		not all modules, 2 if set for all modules. """
		state = 0
		count = 0
		for module in self.modules_flat:
			if int(module.get_state_powered(server_status)):
				state = 1
				count += 1
		if count == len(self.modules_flat):
			state = 2

		return state

	def __del__(self):
		print "Fan wall deleted"


