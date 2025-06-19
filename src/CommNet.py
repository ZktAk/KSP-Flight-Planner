from Missions import Orbit
import Antennas
from Bodies import *

DSN_tiers = {1:2*pow(10,9), 2:50*pow(10,9), 3:250*pow(10,9)}
# DSN_tier = 2
# DSN = DSN_tiers[DSN_tier]



class Satellite(Orbit):
	def __init__(self, body, p_alt, a_alt, inc, power, DSN):
		super().__init__(body, p_alt, a_alt, inc)
		self.batt = power
		self.charge = power
		self.antennas = []
		self.antenna_power = 0
		self.relay_power = 0
		self.range = 0
		self.signal_stength = 0
		self.DSN = DSN


	def add_antenna(self, antenna):
		self.antennas.append(antenna)
		self._combined_antenna_power()
		self._combined_relay_power()
		self._range()
		self.direct_strength()


	def _combined_antenna_power(self):
		c_numerator = sum(antenna.power * antenna.compatibility for antenna in self.antennas)
		sum_power = sum(antenna.power for antenna in self.antennas)
		max_power = max(antenna.power for antenna in self.antennas)

		c = c_numerator / sum_power
		total_power = max_power * pow(sum_power / max_power, c)
		self.antenna_power = total_power


	def _combined_relay_power(self):		
		sum_power = sum(antenna.power for antenna in self.antennas if antenna.is_relay)
		if sum_power > 0:
			c_numerator = sum(antenna.power * antenna.compatibility for antenna in self.antennas if antenna.is_relay)
			max_power = max(antenna.power for antenna in self.antennas if antenna.is_relay)
	
			c = c_numerator / sum_power
			total_power = max_power * pow(sum_power / max_power, c)
			self.relay_power = total_power
	
	def _range(self):
		r = pow(self.DSN * self.antenna_power, 0.5)
		self.range = r

	def direct_strength(self):
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
			peri_distance = abs(Kerbin().r_p - body().r_p)
			apo_distance = abs(Kerbin().r_a - body().r_a)

			min_distance = min(peri_distance, apo_distance)
			max_distance = max(peri_distance, apo_distance)


		x_min = 1 - (min_distance / self.range)
		x_max = 1 - (max_distance / self.range)

		min_stength = -2*pow(x_min,3) + 3*pow(x_min,2)
		max_stength = -2 * pow(x_max, 3) + 3 * pow(x_max, 2)

		self.signal_stength = min_stength
		return max_stength, min_stength

class CommNet:
	def __init__(self, tier=1):
		self.tier = tier
		self.satellites = []

	def closest_relay(self):
		pass

# Example usage
def Test_comms():
	new = Satellite(Mun, 50_000, 50_000, 0, 14_000, DSN_tiers[1])
	new.add_antenna(Antennas.Communotron_16)
	new.add_antenna(Antennas.Communotron_16)
	max, min = new.direct_strength()
	print(f'\nMax %: {round(max*100)}%\nMin %: {round(min*100)}%')
