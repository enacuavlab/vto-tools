from connectedObjects import ConnectedObjects

class Client(ConnectedObjects):
	def __init__(self, facility, ip, client_id, name):
		super(Client, self).__init__()
		self.facility = facility
		self.ip_addr = ip
		self.id = client_id
		self.name = name
		self.life_points = self.facility.max_life_points
		self.is_connected = 1
		self.token_request = 0
		self.in_charge = 0 # Usefull only for client side

		self.cmd_powered = 0
		self.cmd_send_rpm = 0

	def decayLifePoints(self):
		super(Client, self).decayLifePoints()
		if self.life_points == 0:
			self.facility.removeClient(self.ip_addr)
			self.__del__()

	def __del__(self):
		self.facility.addToPrintBuff("[CLIENT] Client with IP : " + self.ip_addr + "deleted.")
