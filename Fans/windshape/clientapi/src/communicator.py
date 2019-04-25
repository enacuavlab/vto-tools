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

import dbapi
import socket
import time
#from datetime import datetime useless I think...
from threading import Timer
#import cPickle
import shutil #usefull to copy the config file in /var/www/html

def initDb(facility):
	
	# Connects to database
	con, cur = dbapi.openDb(facility.db_access)

	#-----------------------------------------------------------------
	# Creations of tables
	#-----------------------------------------------------------------
	# Get wanted row for modules table and create empty table "modules"
	module_rows = facility.fan_walls[0].module_attrs
	dbapi.createTable(con, cur, "modules", module_rows)

	# Get wanted row for sensors table and create empty table "sensors"
	sensor_rows = facility.sensor_attrs
	dbapi.createTable(con, cur, "sensors", sensor_rows)

	# Get wanted row for basic control table and create empty table "basics"
	control_panel_rows = facility.control_panel_attrs
	dbapi.createTable(con, cur, "control", control_panel_rows)

	#-----------------------------------------------------------------
	# Populating of tables
	#-----------------------------------------------------------------
	# Read modules MAC and populate table "modules"
	module_macs = facility.fan_walls[0].module_macs # modulesMac list of string "modID, posY, posX, MAC"
	for i in module_macs:
		i[3] = "'"+i[3]+"'"
		values = str(",".join(i)).strip()
		dbapi.populateTable(con, cur, "modules", "id, pos_y, pos_x, mac_addr",values)

	# Read sensors MAC and populates table "sensors"
	sensor_macs = facility.sensor_macs # modulesMac list of string "sensID, name, MAC"
	for i in sensor_macs:
		i[1] = "'"+i[1]+"'"
		i[2] = "'"+i[2]+"'"
		values = str(",".join(i)).strip()
		dbapi.populateTable(con, cur, "sensors", "id, name, mac_addr", values)

	# Read control panel MAC and populates table "control"
	control_panel_mac = facility.control_panel_mac # basicsMac list of string "basicID, MAC"
	if len(control_panel_mac) > 1:
		control_panel_mac[1] = "'"+control_panel_mac[1]+"'"
		values = str(",".join(control_panel_mac)).strip()
		dbapi.populateTable(con, cur, "control", "id, mac_addr", values)

	# Set pwm, rpm, lifePoints to 0
	z = "'"
	for ifan in range(int(facility.fan_walls[0].fan_number)):
		for ilay in range(int(facility.fan_walls[0].fan_layers)):
			z += "0,"
	z = z[:-1]
	z += "'"

	dbapi.setAllValues(con, cur, "modules", "pwm", z)
	dbapi.setAllValues(con, cur, "modules", "rpm", z)

	con.close()

def storeConfig(facility):
	""" @TODO REMOVE """
	abs_address = "/var/www/html" + facility.config_address
	shutil.copy2('configurations/config.conf', abs_address)

def createSocket(port, broadcast_flag, bind_flag=True):
	# Set socket as UDP and use IPv4
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	if bind_flag:
		# Make the socket reusable in case of inproper closure
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		
		# Allow broadcast
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, broadcast_flag)

		# Block until data available
		sock.setblocking(True)

		sock.settimeout(5) # Blocks for 0.5 seconds, then releases
		
		# Bind to port
		if broadcast_flag:
			sock.bind(('<broadcast>', int(port)))
		else:
			sock.bind(('', int(port)))

	return sock
	
def sendBroadcast(facility):

	print "[THD INIT] Broadcasting thread started..."
	time.sleep(0.01)
	
	# Create sockets for broadcast and answer
	bdcst_sock = createSocket(facility.ports[0], 1) # Sends to all IPs, receive broadcast message (won't be used to receive), on bdcst_port
	
	# Check if there is a missing IP
	while facility.stop_flag == 0:
		t_start = time.time()

		m_miss = 0
		for module in facility.fan_walls[0].modules_flat:
			if len(module.ip_addr) == 0:
				m_miss += 1

		s_miss = 0
		for sensor in facility.sensors:
			if len(sensor.ip_addr) == 0:
				s_miss += 1
		
		c_miss = 0
		if facility.control_panel != None:
			if len(facility.control_panel.ip_addr) == 0:
				c_miss += 1

		if m_miss+s_miss+c_miss > 0:
			if facility.module_verbose == 1:
				bdcst_sock.sendto("Bv\0", ('<broadcast>', int(facility.ports[0])))
				time.sleep(0.001)

			else:
				bdcst_sock.sendto("B\0", ('<broadcast>', int(facility.ports[0])))
				time.sleep(0.001)

 			facility.addToPrintBuff("[BDCSTTH] Broadcast sent. Modules missing : " + str(m_miss) + ", sensors missing : " + str(s_miss) + ", control_panel missing : " + str(c_miss) + ".")

 		t_elapsed = time.time() - t_start
 		if t_elapsed < 1.0/0.5:
			time.sleep(float(4.0 - t_elapsed))

	bdcst_sock.close()
	print "[THD END] Broadcasting thread ended."
	time.sleep(0.01)

def recvAnswer(facility):
	# Listens for answers from nucleo's (M:...) after they received a broadcast, and also listens to new clients
	print "[THD INIT] Broadcast answer listening thread started..."
	time.sleep(0.01)

	answer_sock = createSocket(facility.ports[1], 0) # Receive from all IPs, send to port specified later (won't be used to send), on answer_port

	while facility.stop_flag == 0:	
		recvd = ''
		try:
			recvd, addr = answer_sock.recvfrom(8192) #addr is a tuple (ip, port)
			time.sleep(0.001)
		except:
 			#facility.addToPrintBuff("[ANSWERTH] Timeout!")
 			continue

		# Safety
		if len(recvd) == 0:
			continue

		IP = addr[0]
		
		# Module's answer (Module state)
		if recvd[0] == 'M':
			
			try:
				# Get data of interest from the incomming message
				MAC = recvd[2:recvd.index('\0')].strip()
			except:
				facility.addToPrintBuff("[ANSWERTH] Wrong message MAC from nucleo !")
				continue

			done = 0
			for module in facility.fan_walls[0].modules_flat:
				if module.mac_addr == MAC:
					module.setIP(IP)
					done = 1 
					break

			if done == 0:
				for sensor in facility.sensors:
					if sensor.mac_addr == MAC:
						sensor.setIP(IP)
						done = 1
						break

			if done == 0:
				if facility.control_panel != None:
					if facility.control_panel.mac_addr == MAC:
						facility.control_panel.setIP(IP)
						break

			facility.addToPrintBuff("[ANSWERTH] IP received : " + str(IP) + " from MAC : " + str(MAC) + ".")
		
	answer_sock.close()
	print "[THD END] Broadcast answer listening thread ended."
	time.sleep(0.01)

def updateDb(facility):
	
	print "[THD INIT] Database update thread started..."
	time.sleep(0.01)

	con, cur = dbapi.openDb(facility.db_access)

	while facility.stop_flag == 0:
		t_start = time.time()

		# Update modules in database
		dbapi.updateModules(con, cur, facility)

		# Update sensors in database
		dbapi.updateSensors(con, cur, facility)

		# Update control panels in database
		dbapi.updateControl(con, cur, facility)

		t_elapsed = time.time()-t_start
		if t_elapsed< 1.0/facility.frequency:
			time.sleep(float(1.0/facility.frequency - t_elapsed))

	con.close()
	print "[THD END] Database update thread ended."
	time.sleep(0.01)

def sendOrder(facility):

	print "[THD INIT] Order sending thread started."
	time.sleep(0.01)
	
	# Create sockets for order et data receiving from modules
	send_sock = createSocket(facility.ports[2], 0) # Sends to any IPs in send_port
	
	while facility.stop_flag == 0:
		t_start = time.time()
		# Send orders to modules
		for module in facility.fan_walls[0].modules_flat:
			if len(module.ip_addr) == 0:
				continue

			else:
				cmd = "O:{};{};{};{};{}\0".format(int(module.cmd_powered), int(module.cmd_flashing), int(module.cmd_reboot), int(module.cmd_send_rpm), module.getPWMstr())
				#print "SENDING TO MODULE: ", cmd
				try:
					a = send_sock.sendto(cmd, (module.ip_addr, int(facility.ports[2])))
				except:
					facility.addToPrintBuff('[SENDTICK] ERROR: CANNOT SEND '+str(cmd)+' TO MODULE '+str(module.ip_addr)+'.')
					pass

				module.decayLifePoints()

		# Send orders to sensors
		for sensor in facility.sensors:
			if len(sensor.ip_addr) == 0:
				continue

			else:
				cmd = "O:{};{};{};{}\0".format(int(sensor.cmd_send_data), int(sensor.cmd_flashing), int(sensor.cmd_reboot), sensor.sample_rate)
				try:
					send_sock.sendto(cmd, (sensor.ip_addr, int(facility.ports[2])))
				except:
					facility.addToPrintBuff('[SENDTICK] ERROR: CANNOT SEND '+str(cmd)+' TO SENSOR '+str(sensor.ip_addr)+'.')
					pass

				sensor.decayLifePoints()

		# Send order to control panel
		if facility.control_panel != None:
			if len(facility.control_panel.ip_addr) == 0:
				pass

			else:
				cmd = "O:\0"
				try:
					send_sock.sendto(cmd, (control.ip_addr, int(facility.ports[2])))
				except:
					facility.addToPrintBuff('[SENDTICK] ERROR: CANNOT SEND '+str(cmd)+' TO CONTROL PANEL '+str(sensor.ip_addr)+'.')
					pass

				control.decayLifePoints()

		used = time.time() - t_start
		if used < 1.0/facility.frequency:
			time.sleep(float(1.0/facility.frequency - used))
	

	# Send order to stop every module when program quits
	for module in facility.fan_walls[0].modules_flat:
		if len(module.ip_addr) == 0:
			continue
		else:
			cmd = "O:{};{};{};{};{}\0".format('0', '0', '0', '0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
			send_sock.sendto(cmd, (module.ip_addr, facility.ports[2]))
			
	# Send order to stop data acquisition on sensors
	for sensor in facility.sensors:
		if len(sensor.ip_addr) == 0:
			continue

		else:
			cmd = "O:{};{};{};{}\0".format('0', '0', '0', '0')
			send_sock.sendto(cms, (sensor.ip_addr, facility.ports[2]))



	send_sock.close()
	print "[THD END] Order send thread ended."
	time.sleep(0.01)

def recvData(facility):

	print "[THD INIT] Data receiving thread started..."
	time.sleep(0.01)

	recv_sock = createSocket(facility.ports[3], 0) # Receive from all IPs, send to port specified later (won't be used to send), on answer_port

	while facility.stop_flag == 0:
		recvd = ''
		try:
			recvd, addr = recv_sock.recvfrom(8192) #addr is a tuple (ip, port)
			time.sleep(0.001)
		except:
 			# facility.addToPrintBuff("[RECVTH] Timeout!")
 			continue

		# Safety
		if len(recvd) == 0:
			continue
		
		IP = addr[0]

		try:
			# Get data of interest from the incomming message
			data = recvd[2:recvd.index('\0')].strip()
		except:
			facility.addToPrintBuff("[ANSWERTH] Wrong message MAC from nucleo !")
			continue

		if recvd[0] == 'D':
			#print "[RECVTH] recvd: ", recvd
			for module in facility.fan_walls[0].modules_flat:
				if module.ip_addr == IP:		
					datas = data.split(";")			
					module.state_powered = int(datas[0])
					module.state_send_rpm = int(datas[1])
					module.state_flashing = int(datas[2])
					if len(datas)>3:
						module.setRPMstr(datas[3])

					module.life_points = facility.max_life_points
					module.is_connected = 1
				
					break


		elif recvd[0] == 'S':
			for sensor in facility.sensors:
				if sensor.ip_addr == IP:
					sensor.state_send_data, sensor.data1, sensor.data2 = data.split(';')

					sensor.life_points = facility.max_life_points
					sensor.is_connected = 1

					break


		elif recvd[0] == 'C':
			if facility.control_panel != None:
				if facility.control_panel == IP:
					
					facility.control_panel.request_token, pwm = data.split(';')
					facility.control_panel.life_points = facility.max_life_points
					facility.control_panel.is_connected = 1
					
					if facility.control_token == "control_panel":
						for module in facility.fan_walls[0].modules_flat:
							module.setPWMstr(pwm)

					break

	recv_sock.close()
	print "[THD END] Data receiving thread ended."
	time.sleep(0.01)

def trySendClient(facility, socket, cmd, ip, port):
	try:
		socket.sendto(cmd, (ip, int(port)))
		#time.sleep(0.00001)
	except:
		facility.addToPrintBuff("[SENDCLIENT] ERROR: CANNOT SEND CONTROL PANELS TO CLIENT!")	

def sendClient(facility):
	print "[THD INIT] Client sending thread started."
	time.sleep(0.01)
	
	# Create sockets for broadcast and answer
	send_client_socket = createSocket(facility.ports[4], 0, bind_flag=False) # Sends to any IPs in send_port

	while facility.stop_flag == 0:
		t_start = time.time()
		# Updates token every 1/frequency sec. (not really related to tickSend, but has to be done somewhere)
		facility.updateControlToken()

		if len(facility.clients) > 0:
			for client in facility.clients:
				client.decayLifePoints()
				# Get message to send to client regarding Modules
				mess_module = facility.getMsgModule("client", client)

				# Get message to send to client regarding Sensors
				mess_sensor = facility.getMsgSensor("client", client)

				#Get message to send to client regarding general status
				mess_status = facility.getMsgStatus("client", client)

				trySendClient(facility, send_client_socket, mess_status, client.ip_addr, facility.ports[4])

				trySendClient(facility, send_client_socket, mess_module, client.ip_addr, facility.ports[4])
				
				trySendClient(facility, send_client_socket, mess_sensor, client.ip_addr, facility.ports[4])

		t_elapsed = time.time() - t_start
		if t_elapsed < 1.0/facility.frequency:
			time.sleep(float(1.0/facility.frequency - t_elapsed))

	send_client_socket.close()
	print "[THD END] Clients sending thread ended."

def recvClient(facility):

	print "[THD INIT] Client receiving thread started..."
	time.sleep(0.01)
	
	recv_client_sock = createSocket(facility.ports[5], 0) # Receives from any IPs on recv_port
	send_address_sock =createSocket(facility.ports[4], 0, bind_flag=False)

	while facility.stop_flag == 0:
		recvd = ''
		try:
			recvd, addr = recv_client_sock.recvfrom(8192) #addr is a tuple (ip, port)
			time.sleep(0.001)
			IP = addr[0]
		except:
 			#facility.addToPrintBuff("[CLIENTRECVTH] Timeout!")
 			pass

		# Safety
		if len(recvd) == 0:
			continue

		header, msg = recvd.split(":", 1)
		header, client_id = header.split("@")
		msg = msg[0:msg.index('\0')].strip()

		#print ">>>> RECVD FROM @"+str(client_id)+": "+recvd

		if header == "EMERGENCY":
			if msg == "1":
				facility.turnOffFans()
				facility.control_token = "emergency"
			elif msg == "0" and facility.control_token == "emergency":
				facility.control_token = "free"
			continue

		current_client = None
		for client in facility.clients:
			if str(client.id) == str(client_id):
				current_client = client
				client.life_points = facility.max_life_points
				client.is_connected = 1
				break

		if header == "REQUEST_CONNECTION":
			if current_client == None:
				current_client = facility.createClient(IP, client_id, msg)

			# Send pickle even if client already exists, it might need it again (?)...
			sendAddress(send_address_sock, facility, IP, client_id)

		elif header == "STATUS":
			#print "[CLIENTRECVTH]"+msg
			facility.interpretMsgStatus(msg, "server", current_client)

		if current_client and (facility.control_token == current_client.id):
			if header == "MODULE":
				#print "[CLIENTRECVTH] MODULE MSG RECVD"
				#print msg
				facility.interpretMsgModule(msg, "server")

			elif header == "SENSOR":
				#print "[CLIENTRECVTH] SENSOR MSG RECVD"
				facility.interpretMsgSensor(msg, "server")

	recv_client_sock.close()
	print "[THD END] Client order receiving thread ended."
	time.sleep(0.01)

def stopper(facility):
	print "[THD INIT] Stopper thread started..."
	time.sleep(0.01)
	
	stop_sock = createSocket(facility.ports[6], 0)  # Receives from any IPs on recv_port

	while facility.stop_flag == 0:
		recvd = ''
		try:
			recvd, addr = stop_sock.recvfrom(128)
			time.sleep(0.001)
			print "Received something on stop socket: "+ recvd
		except:
			continue
			#facility.addToPrintBuff("[STOPTH] Timeout or error !")

		# Safety
		if len(recvd) == 0:
			continue

		recvd = recvd.strip()
		if recvd[0:4] == "stop":
			stop_sock.sendto("OK", (addr[0], facility.ports[7]))
			facility.stop_flag = 1

	stop_sock.close()
	print "[THD END] Stoper thread ended."
	time.sleep(0.01)

def sendAddress(sock, facility, ip, client_id):
	'''Send the pickle to the new client who just sent an initial message.'''
	msg = "ADDRESS@"
	msg += str(client_id)+":"
	msg += str(facility.config_address)
	msg += "\0"
	sock.sendto(msg, (ip, int(facility.ports[4])))



