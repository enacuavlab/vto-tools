
from __future__ import print_function
import sys
import os
import subprocess
import socket 
import facility
from threading import Thread
import time
import urllib2
from math import sin, cos, exp, sqrt
import random

FROM_SERVER_PORT = 60333
TO_SERVER_PORT   = 60334

RC_FROM_SERVER_PORT = 60338
RC_TO_SERVER_PORT = 60337

class WindControlApp():
	""" WindControl API offers a set of functions that can be called from a python (2.7)
	script to run WindShape machines in an infinite variety of ways. 

	(1) import this module in your with "import src.windControlAPI" 
	
	(2) create an instance of WindControlApp in your script by calling "wcapi = src.windControlAPI.WindControlApp()"
	
	(3) use any functions of wcapi in your script to control the machine.

	Examples are available if you download the sources of this API from the onboard computer
	at http://192.168.88.40/clientapi/clientapi.zip
	"""

	def __init__(self, SERVER_IP="192.168.88.40", verbose_comm=True):
		""" Constructor """
		self.VERBOSE_COMMUNICATION = verbose_comm

		self.facility = None
		self.fan_wall = None
		self.client   = None

		self.is_link_initialized = False
		self.is_link_active = False

		# Print app title
		version = "2.0"
		date    = "March 2019"
		devteam = "Guillaume Catry, Nicolas Bosson"
		logf('apptitle', (date, version, devteam))
		log('Verbose mode:      '+str(verbose_comm))
		log('Client IP address: '+str(get_ip()))
		log('Server IP address: '+str(SERVER_IP))
		logf('thinline')

		# Create communication sockets 
		self.SERVER_IP = SERVER_IP
		self.FROM_SERVER_PORT = FROM_SERVER_PORT
		self.TO_SERVER_PORT = TO_SERVER_PORT
		self.socket_recv = createSocket('recv', self.SERVER_IP, self.FROM_SERVER_PORT)
		self.socket_send = createSocket('send', self.SERVER_IP, self.TO_SERVER_PORT)

		self.windFunctions = []



	def shutdown(self):
		""" *Control Function* 

		Turn all PWM to 0 and turn off all PSU then wait a sufficent amount of time
		to ensure the orders are sent to the onboard computer (also called server). """
		self.setPWM(0)
		self.stopPSUs()
		time.sleep(1)

	def startPSU(self, id):
		""" *Control Function* 

		Start the power supply unit (PSU) of a given module defined by its 
		module id (int). 

		Args:
			id (int): id of the module
		"""
		module = self.__moduleByID(id)
		module.set_cmd_powered(1)

	def startPSUs(self):
		""" *Control Function* 

		Start all power supply units (PSU). """
		for module in self.fan_wall.modules_flat:
			module.set_cmd_powered(1)

	def stopPSU(self, id):
		""" *Control Function* 

		Stop the power supply unit (PSU) of a given module defined by its 
		module id (int). 

		Args:
			id (int): id of the module
		"""
		module = self.__moduleByID(id)
		module.set_cmd_powered(0)

	def stopPSUs(self):
		""" *Control Function* 

		Stop all power supply units (PSUs). """
		for module in self.fan_wall.modules_flat:
			module.set_cmd_powered(0)

	def togglePSUs(self):
		""" *Control Function* 

		Invert the power state of all Power Supply Units (PSUs). """
		nb_on  = 0
		nf_off = 0
		for module in self.fan_wall.modules_flat:
			state = module.get_state_powered(server_status=True)
			if state:
				nb_on += 1
			else:
				nb_off += 1
		if nb_on > nb_off:
			self.stopPSUs()
		else:
			self.startPSUs()

	def statusPSU(self, id):
		""" *Control Function* 

		Return the status of the power supply unit (PSU) of a given module 
		defined by its module id (int). The returned value is 1 if the PSU is ON, 
		or 0 if the PSU is OFF. 

		Args:
			id (int): id of the module
		"""
		module = self.__moduleByID(id)
		return module.get_state_powered(server_status=True)
		
	def statusPSUs(self):
		""" *Control Function* 

		Return the status of all power supply units (PSUs). Return a flat array of  
		boolean values set to 1 for PSU that are ON, or 0 for PSU that are OFF. 
		"""
		states = []
		for module in self.fan_wall.modules_flat:
			states.append(module.get_state_powered(server_status=True))
		return states

	def startFlashing(self, id):
		""" *Control Function* 

		Enable LED flashing for module defined by id (int). Thie feature allows to 
		identify physically a module or to check visually if a module is responding.

		Args:
			id (int): id of the module
		"""
		module = self.__moduleByID(id)
		module.set_cmd_flashing(True)

	def stopFlashing(self, id):
		""" *Control Function* 

		Disable LED flashing for module defined by module id (int).

		Args:
			id (int): id of the module
		"""
		module = self.__moduleByID(id)
		module.set_cmd_flashing(False)

	def statusFlashing(self, id):
		""" *Control Function* 

		Interrogate and return the status of LED flashing feature for module 
		defined by its id (int).

		Args:
			id (int): id of the module
		"""
		module = self.__moduleByID(id)
		return module.get_state_flashing(server_status=True)

	def startRPMFeature(self):
		""" *Control Function* 

		Enable the counting of RPMs by the microcontrolers onboard of the modules. """
		self.rpmFeature(True)

	def stopRPMFeature(self):
		""" *Control Function* 

		Disable the counting of RPMs by the microcontrolers onboard of the modules. """
		self.rpmFeature(False)
		
	def startLogOBC(self):
		""" *Control Function* 

		Start data logging on the OBC. Files are available at 192.168.88.40/logs. A new folder is created at each start. 
		Use deleteLogsOBC() to delete all the logs."""
		self.facility.cmd_logging = True
		
	def stopLogOBC(self):
		""" *Control Function* 

		Start data logging on the onboard computer. Use deleteLogs() the delete all the logs. """
		self.facility.cmd_logging = False

	def deleteLogsOBC(self):
		""" *Control Function* 

		Delete log folders that are stored on the OBC at 192.168.88.40/logs."""
		self._sendCommand("deletelogs")

	def rebootModule(self, id):
		""" *Control Function* 

		Force the reboot of a given module defined by its module id (int).

		Args:
			id (int): id of the module
		"""
		module = self.__moduleByID(id)
		module.set_cmd_reboot(True)

	def rebootModules(self, id):
		""" *Control Function* 

		Force the reboot of all modules.

		Args:
			id (int): id of the module
		"""
		for module in self.fan_wall.modules_flat:
			module.set_cmd_reboot(True)

	def setPWM(self, pwms):
		""" *Control Function* 

		Sets a given value(s) of PWM to a the fan units.
		
		Args:
			pwms (int): 
				single value set for all fan units.
			pwms (float)
				single value set for all fan units (converted to int).
			pwms (list)
				pwm of each fan changed according to this list of pwms.
		"""
		# Check if pwm is a list
		if type(pwms) == list and len(pwms) > 0:
			shape = self.getShape(pwms)
			if type(shape) == int:
				pwms_flat = pwms
			elif (type(shape) == tuple or type(shape) == list) and len(shape) == 2:
				pwms_flat = self.flattenList(pwms)
			else:
				raise TypeError("setPWM() - if pwms argument is of type list, it must be a 1D or a 2D list, not higher")
				return None

			if len(pwms_flat) != len(self.fan_wall.fan_units_flat):
				raise TypeError("setPWM() - length of pwms list ("+str(len(pwms_flat))+") provided is not equal to the number of fans ("+str(len(self.fan_wall.fan_units_flat))+").")
				return None
			else:
				for i, pwm in enumerate(pwms_flat):
					self.fan_wall.fan_units_flat[i].setPWM(int(pwm))

		# Check if pwm is an int or a float
		elif type(pwms) == int or type(pwms) == float:
			for fan_unit in self.fan_wall.fan_units_flat:
					fan_unit.setPWM(int(pwms))

		# Else the type is wrong
		else:
			raise TypeError("setPWM() - accepted types for pwms argument are \
							 1D list, 2D list, int and float, \
							 not "+str(type(pwms)+"."))
			return None
		return 1

	def getPWM(self, fan_layer=0, server_status=True):
		""" *Control Function* 

		Return a list of PWM (float) values for the entire Facility object.

		Args:
			fan_layer (int): 
				0 (default) to get mean PWM for all fan layers, 1 for upstream fans only, 2 for 
				downstream fans only.
				
		"""
		pwms = []
		for fan_units_line in self.fan_wall.fan_units:
			pwm_line = []
			for fan_unit in fan_units_line:
				if fan_layer == 0:
					pwm = fan_unit.getPWM_mean(server_status)
				else:
					pwm = fan_unit.getPWMs(server_status)[fan_layer-1]
				pwm_line.append(pwm)
			pwms.append(pwm_line)
		return pwms

	def getRPM(self, fan_layer=0):
		""" *Control Function* 
		
		Return a list of RPM (int) values for the entire Facility object.

		Args:
			fan_layer (int): 
				0 (default) to get mean RPM for all fan layers, 1 for upstream fans only, 2 for 
				downstream fans only.
		"""
		rpms = []
		for fan_units_line in self.fan_wall.fan_units:
			rpm_line = []
			for fan_unit in fan_units_line:
				if fan_layer == 0:
					rpm = fan_unit.getRPM_mean()
				else:
					rpm = fan_unit.getRPMs()[fan_layer-1]
				rpm_line.append(rpm)
			rpms.append(rpm_line)
		return rpms

	def rpmFeature(self, state):
		""" *Control Function* 

		Activate or deactivate the counting of RPM onboard of the modules. 
	
		Args:
			state (bool)
				True to activate the RPM counting at the modules and False to 
				deactivate.	
		"""
		for module in self.fan_wall.modules_flat:
			module.set_cmd_send_rpm(state)

	def rpmHigherThan(self, fan_layer=0, rpm_limit=1500):
		""" *Control Function* 

		Return a list of 1 or 0 which shows if fans are running with a RPM higher than 
		a given limit.

		Args:
			fan_layer (int): 
				0 (default) to check for mean RPM, 1 for upstream fans only, 2 for 
				downstream fans only.
			rpm_limit (int)
				rpm limit over which the list values pass to 1. (default 1500)

		"""
		rpms = self.flattenList(self.getRPM(fan_layer=fan_layer))
		checks = [0 for i in range(len(rpms))]

		for i, rpm in enumerate(rpms):
			if rpm >= rpm_limit:
				checks[i] = 1

		return checks

	def rpmVSpwm(self, fan_layer=0, acc_range=0.1):
		""" *Control Function*

		The RPM value of each fan is comapared to its current PWM command. The idea is to
		have a method to check if each fan is running as it should. If the RPM value is in an 
		acceptable range (i.e. RPM = 15000/100 * PWM +/- range) the fan is considered as running
		appropriately which is shown by a 1 in the returned list. If the RPM is out of this range, 
		a 0 is shown in the returned list. """

		# Acceptable range between 0 and 1 where 1 = 100%
		acc_range = acc_range

		# Max RPM for each fan layer (0 being the mean max RPM)
		max_rpm = [13500, 13800, 13200]		

		rpm = self.flattenList(self.getRPM(fan_layer=fan_layer))
		pwm = self.flattenList(self.getPWM(fan_layer=fan_layer, server_status=True))
		max_rpm = max_rpm[fan_layer]
		comparisons = [9 for i in range(len(pwm))]

		for i in range(len(rpm)):

			rpm_exp = expectedRPM(pwm[i], fan_layer=fan_layer)

			# Fan not running at all
			if pwm[i] > 5 and rpm[i] < 100:
				c = 0

			# Fan running but slower that the lower acceptable limit	
			elif rpm[i] < rpm_exp*(1-acc_range/2):
				c = 1

			# Fan running faster than the higher acceptable limit
			elif rpm[i] > rpm_exp*(1+acc_range/2):
				c = 3

			# RPM value is too high to be possible
			elif rpm[i] > 1.2*expectedRPM(100, fan_layer=fan_layer):
				c = 4

			# Fan running appropriately
			else:
				c = 2

			comparisons[i] = c

		return comparisons



	def defineWindFunction(self, literal_function, min=0, max=100):
		""" *Control Function*

		This function makes it possible to control the fans with a mathematical function. 
		Prior to call this function, define a literal expression such as "30*sin(3*x+2*t)+4*y*t" which
		will govern the behavior of the fans. Once a wind function is defined, call startWindFunction()
		to start execution. If needed, stop the wind function at anytime by calling killWindFunction().

		When looking at the fan array from downstream: 
		
		- x is the horizontal axis of the fan array with origin on the center of the extreme left fan column and direction from left to right. 
		
		- y is the vertical axis of the fan array with origin on the center of lowest fan row and direction from bottom to top.
		
		- t is the time. 

		Args:
			literal_function (str)
				A literal (string) mathematical expression written using python syntax. Only 
				allowed variables are x, y and z.
			min (int)	
				Allows to set the lower limit of the function evalutation. Anytime the function 
				evaluation give a pwm lower than this limit, the pwm will be forced at the min value.
			max (int)	
				Allows to set the higher limit of the function evalutation. Anytime the function 
				evaluation gives a pwm higher than this limit, the pwm will be forced at the max value.

		 """
		wf = WindFunction(literal_function, min, max, parent=self)
		self.windFunctions.append(wf)
		return wf

	def startWindFunction(self, windFunction, duration, dt, blocking=True):
		""" *Control Function*

		After a wind function is defined with defineWindFunction(), use this method to start the execution 
		of the wind function. 

		Args:
			windFunction (WindFunction)
				a pre-defined (defineWindFunction()) WindFunction.
			duration (float)
				the duration in seconds of the execution of the function, which is simply the max value of the variable t.
			dt (float)
				the delta of time in seconds between each execution of the function. dt = 0.05 (20Hz) if more that enough
				to have a continuous change of the fan's speed.
			blocking (float) 
				if set to blocking, the script calling this function will wait for the execution of the function to 
				terminate. By setting this arg to False, user script will continue to do things while the wind function 
				is executed. (default True)

		"""
		if type(windFunction) is WindFunction:
			windFunction.runFunction(duration, dt, blocking=True)

	def killWindFunction(self, windFunction=None):
		""" *Control Function*
		
		Call this method to stop the execution of a wind function. """
		if type(windFunction) == WindFunction:
			windFunction.killFunction()
		else:
			for windFunction in self.windFunctions:
				windFunction.killFunction()
 


	def requestToken(self):
		""" *Control Function*

		Use requestToken to have control on the WindShaper. This feature allows to
		manage the priorities in the event where multiple clients try to have the 
		control simultaneously.
		"""
		if self.client and self.is_link_initialized:
			self.client.token_request = 1
		else:
			log("[ERROR] CANNOT REQUEST TOKEN WHILE CONNECTION WITH SERVER IS \
				BROKEN OR NOT ESTABLISHED!")

	def releaseToken(self):
		""" *Control Function*

		Release token so that another client can take control over the WindShaper. 
		This feature allows manage the priorities in the event where multiple 
		clients try to have the control simultaneously. See requestToken() for more
		details.
		"""	
		if self.client:
			self.client.token_request = 0

	def startServerLink(self):
		""" *Control Function*

		Start UDP link between the client program and the server. """

		# __prepareServerLink() WAS MADE PRIVATE AND CAN ONLY BE RUN FROM HERE
		self.__prepareServerLink()

		if self.is_link_initialized:
			self.__startServerComThread()

	def stopServerLink(self):
		""" *Control Function*

		Stop UDP link between the client program and the server and 
		properly kill all communication threads on the client side. 
		"""
		if self.is_link_active:
			self.__endServerComThread()

	def getShape(self, array):
		""" *Utility Function*

		Given an single of multi-dimensional array (list), returns its shape 
		as a tuple, i.e. (ny, nx). 

		Example 1:
		pwm_list_2D = wcapi.getPWM()
		nb_fan_y, nb_fan_x = wcapi.getShape(pwm_list_2D)

		Example 2:
		wcapi.getShape([[1,2,3],[4,5,6])
		>> (2, 3)

		"""
		if type(array) == list:
			# at least 1D array
			if len(array) > 0:
				# at least 2D array	
				if type(array[0]) == list and len(array[0]) > 0:
					# at least 3D
					if type(array[0][0]) == list and len(array[0][0]) > 0:
						return len(array), len(array[0]), len(array[0][0])
					else:
						return len(array), len(array[0])
				else:
					return len(array)
			else:
				return 0
		else:
			return 0

	def getFansDict(self, server_status=True, acc_range=0.1):
		""" *Utility Function*

		Used by the WindControl Navigator interface to pass the required fans attributes
		the client (computer which interprets html in this case). """
		rpm_check = self.rpmVSpwm(fan_layer=0, acc_range=acc_range)

		# Format -> fans_dict = { {1: {'pwm'; 100, "rpm":11200}}, {2: {...}} }
		fan_dict = {}
		if self.fan_wall:
			for i, fan_unit in enumerate(self.fan_wall.fan_units_flat):
				fan_dict[i] = {'pwm': fan_unit.getPWM_mean(server_status), 
							   'rpm': fan_unit.getRPM_mean(),
							   'rpm_check': rpm_check[i]} 
		return fan_dict

	def flattenList(self, list_to_flatten):
		""" *Utility Function*

		Given a 2D list, return a flat 1D list.  """
		flat_list = [item for sublist in list_to_flatten for item in sublist]
		return flat_list

	def getFacility(self):
		""" *WindControl Object Stucture Function*

		Return the Facility object currently defined on the server. """
		return self.facility

	def getFanWall(self):
		""" *WindControl Object Stucture Function*

		Return FanWall object currently defined on the server. 
		In this verstion, there is a unique FanWall for each Facility. """
		return self.fan_wall

	def getModules(self, flat=False):
		""" *WindControl Object Stucture Function*

		Return a list 2D of Module objects of the same shape as the physical disposition 
		of the modules.
		
		Args:
			flat (bool): 
				if True, convert the 2D list into a flat list (default False).
		"""
		if flat:
			return self.fan_wall.modules_flat
		return self.fan_wall.modules

	def getModule(self, id):
		""" *WindControl Object Stucture Function*

		Return an unique module object corresponding to the module ID given as argument.
		
		Args:
			id (int)
				the ID of the module to be returned.
		"""
		for module in self.fan_wall.modules_flat:
			if module.id == int(id):
				return module

	def getFanUnits(self, flat=False):
		""" *WindControl Object Stucture Function*

		Return a list 2D of FanUnit objects of the same shape as the physical disposition 
		of the fan units.
		
		Args:
			flat (bool): 
				if True, convert the 2D list into a flat list (default False).
		"""
		if flat:
			return self.fan_wall.fan_units_flat
		return self.fan_wall.fan_units

	def wakeOnLan(self, v=True):
		""" *Onboard Computer Control Function*

		Send a "magic paquet" on the network to remotely turn the onboard computer on.""" 
		log("Sending wake-on-LAN request...", v=v)
		sock = createSocket('send', "192.168.88.255", 7)
		server_mac = "54:bf:64:9c:96:24"
		mac_bytes = server_mac.replace(":", "").decode("hex")

		# Wake on LAN message : FF FF FF FF FF FF + 16x MAC address
		mess = '\xff' * 6 + mac_bytes * 16
		try:
			sock.sendto(mess, ('192.168.88.255', 7))
		except:
			log("Error, can't wake-on-LAN.", v=v)
			sock.close()
			return

		log("Wake-on-LAN paquet sent. Waiting for the onboard computer to be ready...", v=v)
		self.checkPing()
		sock.close()

	def checkPing(self, v=True):
		""" *Onboard Computer Control Function*

		Ping the onboard computer to check if it's online. After 100 fails, the function quits."""
		log("Checking obc status...", v=v)
		obc_on = False
		iteration = 0
		while obc_on == False and iteration < 100:
			iteration += 1
			log("("+str(iteration)+"/100)", v)
			response = os.system("ping -c 1 " + self.SERVER_IP)
			if response == 0:
				obc_on = True
				log("Successfully pinged the onboard computer!", v=v)
			else:
				time.sleep(1)

	def checkServiceStatus(self, v=True):
		""" *Onboard Computer Control Function*

		Check if WindShape service is correctly running on the onboard computer."""
		reply = self._sendCommand('servicestatus')
		if reply == 'servicerunning':
			log("Service correctly running.", v=v)
			return True
		else:
			log("Service not running. Use startService() to start it.", v=v)
			return False

	def startService(self):
		""" *Onboard Computer Control Function*

		Start WindShape service on the onboard computer. This service starts automatically, 
		and should always be running."""
		self._sendCommand('startservice')

	def restartService(self):
		""" *Onboard Computer Control Function*

		Restart WindShape service on the onboard computer. Use this function if the machine
		doesn't respond to controls."""
		self._sendCommand('restartservice')

	def stopService(self):
		""" *Onboard Computer Control Function*

		Stop WindShape service on the onboard computer. Only usefull for bug correction.
		If the service is stopped, the fan wall won't respond."""
		self._sendCommand('stopservice')

	def turnComputerOff(self):
		""" *Onboard Computer Control Function*

		Turn off the onboard comptuer."""
		# First, make sure the fans and the power supplies are off:
		self.shutdown()
		# Then, shutdown the comptuer.
		self._sendCommand("shutdown")

	def __prepareServerLink(self, server_address = 'localhost', client_name = 'api'):
		""" @TODO REPLACE

		Initiate the connection with the server. Must be run before startServerLink() is called.
		Args:
			server_address (str): 
				IP address of the server to connect to.
		"""
		logf('title', "initializing connection with the server", v=self.VERBOSE_COMMUNICATION)


		self.client_id = str(random.randint(1000,10000))

		facility_object = initiateConnectionWithServer(self, self.socket_recv, self.socket_send,
						  self.SERVER_IP, self.TO_SERVER_PORT, self.FROM_SERVER_PORT, self.VERBOSE_COMMUNICATION)
		
		if facility_object == -1:
			return sys.exit("Process terminated.")

		client_ip = get_ip()
		

		facility_object.createClient(client_ip, self.client_id, client_name)
		

		self.__setFacility(facility_object)
		self.is_link_initialized = True

		logf('thinline', v=self.VERBOSE_COMMUNICATION)
		logf('newline', v=self.VERBOSE_COMMUNICATION)

	def _sendCommand(self, cmd, v=True):
		""" *Private method, do not use externally.* 
		Send a command to the Remote Control Service that runs on the onboard computer.
		"""
		if v:
			log("Sending command "+cmd+" to the onboard computer...", v=v)
		sock = createSocket("recv", self.SERVER_IP, port=RC_FROM_SERVER_PORT)

		sock.sendto(cmd, (self.SERVER_IP, RC_TO_SERVER_PORT))

		reply = ''
		try:
			reply, addr = sock.recvfrom(1024)
		except:
			pass

		if reply == '':
			if v:
				log("Server not responding. Try again.", v=v)
		else:
			if v:
				log("Successfully sent command.", v=v)

		sock.close()
		if v:
			pass
			#self.log_separator()  
		return reply  

	def __setFacility(self, facility_object):
		""" *Private method, do not use externally.* """
		self.facility = facility_object
		self.fan_wall = facility_object.fan_walls[0]
		self.client = facility_object.clients[0]

	def __startServerComThread(self):
		""" *Private method, do not use externally.* """
		self.is_link_active = True
		logf('title', "starting comminication with server", v=self.VERBOSE_COMMUNICATION)
		client_thread = Thread(target=clientThread, args=(self, self.facility, self.socket_recv, self.socket_send, 
						self.SERVER_IP, self.TO_SERVER_PORT, self.FROM_SERVER_PORT, self.VERBOSE_COMMUNICATION))
		client_thread.setDaemon(True)
		client_thread.start()
		
	def __endServerComThread(self):
		""" *Private method, do not use externally.* """
		self.is_link_active = False
		time.sleep(0.5)
		log('[CLITH] communication with server terminated.', v=self.VERBOSE_COMMUNICATION)
		logf('thinline', v=self.VERBOSE_COMMUNICATION)
		logf('newline', v=self.VERBOSE_COMMUNICATION)

	def __moduleByID(self, id):
		for module in self.fan_wall.modules_flat:
			if int(module.id) == int(id):
				return module
		raise ValueError("Module with ID "+str(id)+" doesn't exist.")

###############################################################################
# WIND FUNCTIONS API
###############################################################################

class WindFunction(object):
	def __init__(self, literal_function, min=0, max=100, parent=None):
		self.literal_function = literal_function
		self.min = min
		self.max = max
		self.wcapi = parent
		self.functionThread = None
		self.is_running = False

	def evaluate(self, x=0, y=0, t=0):
		exec("result="+str(self.literal_function))
		if result < self.min:
			return self.min
		elif result > self.max:
			return self.max
		return result

	def killFunction(self):
		self.is_running = False

	def runFunction(self, duration, dt, blocking=True):
		self.is_running = True
		self.functionThread = Thread(target=self.timeIt, args=(duration, dt))
		self.functionThread.setDaemon(True)
		self.functionThread.start()
		if blocking:
			self.functionThread.join()

	def timeIt(self, duration, dt):
		""" For each time step, return an evaluation of the WindFuction. """
		print("WIND FUNCTION STARTED...")
		t_start = time.time()
		t_current = 0
		trig = 0
		while t_current < duration and self.is_running:
			if t_current >= trig:
				for fan_unit in self.wcapi.fan_wall.fan_units_flat:
					x, y = fan_unit.coords
					pwm = self.evaluate(x, y, t_current)
					fan_unit.setPWM(int(pwm))
				trig += dt
			t_current = time.time() - t_start
		print("END OF WIND FUNCTION.")

###############################################################################
# PLACE THE FOLLOWING CODE IN A DEDICATED MODULE ON THE CLIENT SIDE.
###############################################################################


def createSocket(direction, ip, port):
	""" Create and return a socket. If direction='send' the socket is not
	bind to any port. """
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	if direction == 'out' or direction == 'send' :
		return sock
	sock.bind(('', port))
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
	sock.settimeout(5)
	return sock

def initiateConnectionWithServer(parent, socket_recv, socket_send, server_ip, to_server_port, from_server_port, v):
	""" Handshake with the server to establish UDP connection.  """

	log("[INITH] connecting with server...", v=v)
	connection_established = False
	
	t_start = time.time()
	i_attempts = 1
	n_attempts = 3
	attempting = 1

	while not connection_established and attempting:

		# if time.time()-t_start >= 2:
		# 	if i_attempts == n_attempts:
		# 		attempting = 0
		# 		log("[INITH] Failed to launch server program.")
		# 		log("[INITH] Terminating WinndControl API...")
		# 		return -1

		# 	log("[INITH] Server program is not running.")
		# 	if server_ip == get_ip():
		# 		log("[INITH] Attempting to launch server program "+str(i_attempts)+"/"+str(n_attempts-1)+"...")
		# 		s = subprocess.call(["cd ~/windcontrol/server && python server.py"])
		# 		log(s, v=True)
		# 	else:
		# 		log("[INITH] Can't run program on a distant computer...")
		# 		log("[INITH] Please run the command - ssh ws_user@192.168.88.40:windcontrol/server/ && python server.py ")
		# 		return -1

		# 	i_attempts += 1

		# Send an hello message
		handshake_msg = "REQUEST_CONNECTION@"+str(parent.client_id)+":no_message\0"
		socket_send.sendto(handshake_msg, (server_ip, to_server_port))

		# Check if status message is reveived
		try:	
			msg_from_server, addr = socket_recv.recvfrom(128)
			msg_header, msg_content = msg_from_server.split(":", 1)
			msg_header, received_client_id = msg_header.split("@")
			if str(received_client_id) != str(parent.client_id):
				continue
		except:
			continue

		if msg_header == "ADDRESS":

			# Check if there is a "\0" in the message and if yes remove it
			if "\0" in msg_content:
				msg_content, _ = msg_content.split("\0") 

			# Handshake successful
			log("[INITH] successful handshake with server with address "+str(addr)+".", v=v)
			log("[INITH] handshake reply: "+str(msg_content), v=v)

			# unpickle the Facility object from server
			#pickle_file = "http://"+SERVER_IP+"/"+msg_content
			#pk_file = urllib2.Request(pickle_file)
			#facility = src.pickler.unpickle_object(pk_file)
			#print(facility)

			server_file = "http://"+server_ip+"/config.conf"
			client_file = "./configurations/config.conf"
			downloadFile(server_file, client_file)

			facility_object = facility.Facility(client_file)

			log("[INITH] Facility object successfully copied from server.", v=v)

			connection_established = True

	return facility_object

def clientThread(parent, facility_object, socket_recv, socket_send, server_ip, to_server_port, from_server_port, v=False):
	""" Function that modifies the current values of global object
	facility during runtime. """
	while parent.is_link_active:

		# Check if status message is reveived
		try:	
			msg_from_server, addr = socket_recv.recvfrom(4096)
			#log(msg_from_server)
			msg_header, msg_content = msg_from_server.split(":", 1)
		except:
			#log("[CLITH] Waiting for server...")
			continue

		msg_header, msg_content = msg_from_server.split(":", 1)
		msg_header, received_client_id = msg_header.split("@")
		if received_client_id != parent.client.id:
			continue
		msg_content.strip()

		reply = None
		if msg_header == "ADDRESS":
			log("[CLITH] ADDRESS message recvd.", v=v)

		elif msg_header == "STATUS":
			log("[CLITH] STATUS message recvd.", v=v)
			facility_object.interpretMsgStatus(msg_content, 'client')
			reply = facility_object.getMsgStatus('server', parent.client)
			
		elif msg_header == "MODULE":
			log("[CLITH] MODULE message recvd.", v=v)
			facility_object.interpretMsgModule(msg_content, 'client')
			reply = facility_object.getMsgModule('server', parent.client)

		elif msg_header == "SENSOR":
			log("[CLITH] SENSOR message recvd.", v=v)
			facility_object.interpretMsgSensor(msg_content, 'client')
			reply = facility_object.getMsgSensor('server', parent.client)
			
		if reply:
			socket_send.sendto(reply, (server_ip, to_server_port))
			log("[CLITH] COMMAND SENT: \n ", v=v)
			logf('modules_data', reply, v=v)

def log(text, client_type='api', log_type='console', log_time=False, v=True):
	if v:
		if client_type == 'navigator':
			print(text, file=sys.stderr)

		else:
			if log_type == 'console':
				print(text)
			elif log_type == 'file':
				pass

def logf(feature, parameter=None, client_type='api', log_type='console', log_time=False, v=True):

	feature_width = 80

	if feature == 'thinline':
		thinline = ""
		for i in range(feature_width):
			thinline+="-"
		log(thinline, client_type=client_type, log_type=log_type, log_time=log_time, v=v)

	if feature == 'thickline':
		thickline = ""
		for i in range(feature_width):
			thickline+="="
		log(thickline, client_type=client_type, log_type=log_type, log_time=log_time, v=v)

	if feature == 'title':
		logf('thinline', client_type=client_type, log_type=log_type, log_time=log_time, v=v)
		title = "| "+str(parameter).upper()
		l = len(title)
		for i in range(feature_width-l):
			title += " "
		title = title[:-1]+"|"
		log(title, client_type=client_type, log_type=log_type, log_time=log_time, v=v)
		logf('thinline', client_type=client_type, log_type=log_type, log_time=log_time, v=v)

	if feature == 'multilines_title':
		logf('thickline', client_type=client_type, log_type=log_type, log_time=log_time, v=v)
		for p in parameter:
			title = "# "+str(p)
			l = len(title)
			for i in range(feature_width-l):
				title += " "
			title = title[:-1]+"#"
			log(title, client_type=client_type, log_type=log_type, log_time=log_time, v=v)
		logf('thickline', client_type=client_type, log_type=log_type, log_time=log_time, v=v)

	if feature == "newline":
		log("\n", client_type=client_type, log_type=log_type, log_time=False, v=v)

	if feature == 'apptitle':
		logf('thickline', client_type=client_type, log_type=log_type, log_time=log_time, v=v)
		date, version, devteam = parameter
		app_title = ["WindControl App",
					 "---------------",
					 " _ _ _ _       _ _____ _               ",
					 "| | | |_|___ _| |   __| |_ ___ ___ ___ ",
					 "| | | | |   | . |__   |   | .'| . | -_|",
					 "|_____|_|_|_|___|_____|_|_|__,|  _|___|",
					 "                              |_|      ",
					 "Version "+str(version)+" - "+str(date)+" - Copyright WindShape LLC Geneva ",
					 "Developed by: "+str(devteam)
					 ]
		for line in app_title:
			title = "# "+str(line)
			l = len(title)
			for i in range(feature_width-l):
				title += " "
			title = title[:-1]+"#"
			log(title, client_type=client_type, log_type=log_type, log_time=log_time, v=v)
		logf('thickline', client_type=client_type, log_type=log_type, log_time=log_time, v=v)

	if feature == 'modules_data':
		_, parameter = parameter.split(":", 1)
		modules_data = parameter.split("|")
		for module_data in modules_data:
			log(module_data, client_type=client_type, log_type=log_type, log_time=log_time, v=v)

def downloadFile(url, src):

	# Disable the proxy
	proxy_handler = urllib2.ProxyHandler({})
	opener = urllib2.build_opener(proxy_handler)

	# Open the url
	try:
		f = opener.open(url)

		# Open our local file for writing
		with open(src, "w") as local_file:
			local_file.write(f.read())

	# Handle errors
	except urllib2.HTTPError, e:
		log("HTTP Error:"+str(e.code)+" "+str(url))
	except urllib2.URLError, e:
		log("URL Error:"+str(e.reason)+" "+str(url))
					  
def get_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		# doesn't even have to be reachable
		s.connect(('10.255.255.255', 1))
		IP = s.getsockname()[0]
	except:
		IP = '127.0.0.1'
	finally:
		s.close()
	return IP

def expectedRPM(pwm, fan_layer=0):
	delta_pwm = 5
	pwm_discret = [i*5 for i in range(100/delta_pwm+1)]

	rpm_u = [0,
			1406,
			2037,
			2730,
			3355,
			4087,
			4706,
			5354,
			6058,
			6620,
			7213,
			7801,
			8474,
			9158,
			9790,
			10463,
			11147,
			11800,
			12517,
			13174,
			13682]

	rpm_d = [0,
			1348,
			1968,
			2639,
			3244,
			3848,
			4521,
			5092,
			5776,
			6340,
			6904,
			7478,
			8124,
			8767,
			9412,
			10051,
			10696,
			11334,
			11982,
			12855,
			13147]

	rpm_exp = []
	rpm_m_exp, rpm_u_exp, rpm_d_exp = [-1, -1, -1]

	for i in range(len(pwm_discret)-1):
		if pwm == pwm_discret[i]:
			rpm_u_exp = rpm_u[i]
			rpm_d_exp = rpm_d[i]
			rpm_m_exp = (rpm_u_exp+rpm_d_exp)/2
			break
		elif pwm >= pwm_discret[i] and pwm <= pwm_discret[i+1]:
			add_pwm = pwm-pwm_discret[i]
			rpm_u_exp = add_pwm*(rpm_u[i+1]-rpm_u[i])/delta_pwm+rpm_u[i]
			rpm_d_exp = add_pwm*(rpm_d[i+1]-rpm_d[i])/delta_pwm+rpm_d[i]
			rpm_m_exp = (rpm_u_exp+rpm_d_exp)/2
			break

	rpm_exp = [rpm_m_exp, rpm_u_exp, rpm_d_exp]

	return rpm_exp[fan_layer]

