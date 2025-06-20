from Missions import Orbit
import Antennas
from Bodies import *

class Satellite():
	def __init__(self, orbit, power, DSN):
		self.orbit = orbit
		self.batt = power
		self.charge = power
		self.antennas = []
		self.d_power = 0
		self.r_power = 0
		self.d_range = 0
		self.r_range = 0
		self.d_signal_strength = 0
		self.r_signal_strength = 0
		self.DSN = DSN


	def add_antenna(self, antenna):
		self.antennas.append(antenna)
		self._combined_antenna_power()
		self._combined_relay_power()
		self._direct_range()
		self._relay_range()
		self.direct_strength()


	def _combined_antenna_power(self):
		c_numerator = sum(antenna.power * antenna.compatibility for antenna in self.antennas)
		sum_power = sum(antenna.power for antenna in self.antennas)
		max_power = max(antenna.power for antenna in self.antennas)

		c = c_numerator / sum_power
		total_power = max_power * pow(sum_power / max_power, c)
		self.d_power = total_power


	def _combined_relay_power(self):		
		sum_power = sum(antenna.power for antenna in self.antennas if antenna.is_relay)
		if sum_power > 0:
			c_numerator = sum(antenna.power * antenna.compatibility for antenna in self.antennas if antenna.is_relay)
			max_power = max(antenna.power for antenna in self.antennas if antenna.is_relay)
	
			c = c_numerator / sum_power
			total_power = max_power * pow(sum_power / max_power, c)
			self.r_power = total_power
	
	def _direct_range(self, target=None):
		target = self.DSN if target is None else target
		r = pow(target * self.d_power, 0.5)
		self.d_range = r

	def _relay_range(self, target=None):
		target = self.DSN if target is None else target
		r = pow(target * self.r_power, 0.5)
		self.r_range = r
		return

	def relay_range(self, target_power=None):
		target_power = self.DSN if target_power is None else target_power
		r = pow(target_power * self.r_power, 0.5)
		return r

	def direct_strength(self):
		min_distance = max_distance = 0
		body = self.orbit.parent

		if body is Kerbin:
			min_distance = self.orbit.p_alt
			max_distance = self.orbit.a_alt
		elif body().parent is Kerbin:
			r_p = self.orbit.p_alt + body().radius
			r_a = self.orbit.a_alt + body().radius

			min_distance = (body().r_p - body().parent().radius) - r_a
			max_distance = (body().r_a - body().parent().radius) + r_a

		elif body().parent is Kerbol:
			peri_distance = abs(Kerbin().r_p - body().r_p)
			apo_distance = abs(Kerbin().r_a - body().r_a)

			min_distance = min(peri_distance, apo_distance)
			max_distance = max(peri_distance, apo_distance)


		x_min = 1 - (min_distance / self.d_range)
		x_max = 1 - (max_distance / self.d_range)

		min_strength = -2*pow(x_min,3) + 3*pow(x_min,2)
		max_strength = -2 * pow(x_max, 3) + 3 * pow(x_max, 2)

		self.d_signal_strength = min_strength
		return max_strength, min_strength


	def relay_strength(self):
		min_distance = max_distance = 0
		body = self.orbit.parent

		if body is Kerbin:
			min_distance = self.orbit.p_alt
			max_distance = self.orbit.a_alt
		elif body().parent is Kerbin:
			r_p = self.orbit.p_alt + body().radius
			r_a = self.orbit.a_alt + body().radius

			min_distance = (body().r_p - body().parent().radius) - r_a
			max_distance = (body().r_a - body().parent().radius) + r_a

		elif body().parent is Kerbol:
			peri_distance = abs(Kerbin().r_p - body().r_p)
			apo_distance = abs(Kerbin().r_a - body().r_a)

			min_distance = min(peri_distance, apo_distance)
			max_distance = max(peri_distance, apo_distance)

		x_min = 1 - (min_distance / self.r_range)
		x_max = 1 - (max_distance / self.r_range)

		min_strength = -2 * pow(x_min, 3) + 3 * pow(x_min, 2)
		max_strength = -2 * pow(x_max, 3) + 3 * pow(x_max, 2)

		self.r_signal_strength = min_strength
		return max_strength, min_strength


class CommNet:
	def __init__(self, tier=1):
		self.tier = tier
		self.DSN = {1:2*pow(10,9), 2:50*pow(10,9), 3:250*pow(10,9)}[tier]
		self.satellites = []
		self._satellite = None


	def add_satellite(self, satellite):
		self._satellite = satellite
		self.satellites.append(satellite)


	def max_distance_between(self, sat_a, sat_b):

		if sat_a


	def has_signal(self, satellite, target_strength=0.7):
		visited = set()
		path, strength = self._find_signal_path(satellite, target_strength, visited)
		if path:
			return path, strength
		return None

	def _find_signal_path(self): pass

	def signal_strength(self, sat, target):
		target_power = target.r_power
		sat_range = sat.relay_range(target_power)



		
		
		distance = sat.distance_to(target)
		if distance == 0 or sat.d_power == 0:
			return 0
		x = 1 - (sat.d_range / distance)
		return max(0, -2 * x**3 + 3 * x**2)
	

# Example usage
def Test_comms():
	orbit = Orbit(Mun, 50_000, 50_000, 0)
	new = Satellite(orbit, 14_000, {1:2*pow(10,9), 2:50*pow(10,9), 3:250*pow(10,9)}[1])
	new.add_antenna(Antennas.Communotron_16)
	new.add_antenna(Antennas.Communotron_16)
	max, min = new.direct_strength()
	print(f'\nMax %: {round(max*100)}%\nMin %: {round(min*100)}%')
