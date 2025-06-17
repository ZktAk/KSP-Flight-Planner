from Missions import Orbit

class Relay(Orbit):
	def __init__(self, body, p_alt, a_alt, inc, power):
		super().__init__(body, p_alt, a_alt, inc)
		self.power = power

class CommNet:
	def __init__(self, DNS_level=1):
		self.DNS = 1
		self.relays = []
