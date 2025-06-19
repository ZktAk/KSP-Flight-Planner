from Missions import Orbit
import Antennas
from Bodies import *

class Satellite(Orbit):
	def __init__(self, body, p_alt, a_alt, inc, power):
		super().__init__(body, p_alt, a_alt, inc)
		self.batt = power
		self.charge = power
		self.antennas = []
		self.antenna_power = 0
		self.relay_power = 0
		self.range = 0
		self.signal_stength = 0


	def add_antenna(self, antenna):
		self.antennas.append(antenna)


	def antenna_stength(self):
		c_numerator = sum(antenna.power * antenna.compatibility for antenna in self.antennas)
		sum_power = sum(antenna.power for antenna in self.antennas)
		max_power = max(antenna.power for antenna in self.antennas)

		c = c_numerator / sum_power
		total_power = max_power * pow(sum_power / max_power, c)
		self.antenna_power = total_power
		return total_power


	def relay_strength(self):
		c_numerator = sum(antenna.power * antenna.compatibility for antenna in self.antennas if antenna.is_relay)
		sum_power = sum(antenna.power for antenna in self.antennas if antenna.is_relay)
		max_power = max(antenna.power for antenna in self.antennas if antenna.is_relay)

		c = c_numerator / sum_power
		total_power = max_power * pow(sum_power / max_power, c)
		self.relay_power = total_power
		return total_power

	def range(self, DSN):
		r = pow(DSN * self.antenna_power, 0.5)
		self.range = r
		return r

	def signal_strength(self):
		min_distance = max_distance = 0
		body = self.body

		if body is Kerbin:
			min_distance = self.p_alt
			max_distance = self.a_alt
		elif body().parent is Kerbin:
			r_p = self.p_alt + body().radius
			r_a = self.a_alt + body().radius

			min_distance = (body().r_p - body().parent().radius) - r_a
			max_distance = (body().r_a - body().parent().radius) + r_a

		elif body().parent is Kerbol:
			min_distance = Kerbin().r_a


		x_min = 1 - (min_distance / self.range)
		x_max = 1 - (max_distance / self.range)

		min_stength = -2*pow(x_min,3) + 3*pow(x_min,2)
		max_stength = -2 * pow(x_max, 3) + 3 * pow(x_max, 2)

class CommNet:
	def __init__(self, tier=1):
		self.tier = tier
		self.satellites = []

	def closest_relay