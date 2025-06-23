from Missions import Orbit
import antenna_types
from Bodies import *

class Satellite():
	def __init__(self, orbit, power, DSN, comm_type='Direct'):
		self.orbit = orbit
		self.batt = power
		self.charge = power
		self.comm_type = comm_type

		self.DSN = DSN
		self.antennas = []
		self.signal_power = 0
		self.signal_range = 0
		self.signal_strength = 0		

	def add_antenna(self, antenna):
		if antenna.is_relay and self.comm_type == 'Direct':
			raise ValueError("Cannot add relay antenna to direct communication satellite")
		elif not antenna.is_relay and self.comm_type == 'Relay':
			raise ValueError("Cannot add direct antenna to relay communication satellite")
			
		self.antennas.append(antenna)
		self._power()
		self._range()
		self._strength()

	def _power(self):
		c_numerator = sum(antenna.power * antenna.compatibility for antenna in self.antennas)
		sum_power = sum(antenna.power for antenna in self.antennas)
		max_power = max(antenna.power for antenna in self.antennas)

		c = c_numerator / sum_power
		total_power = max_power * pow(sum_power / max_power, c)
		self.signal_power = total_power
		

	def _range(self): 
		r = pow(self.DSN * self.signal_power, 0.5)
		self.signal_range = r

	def range(self, target=None):
		target = self.DSN if target is None else target
		r = pow(target * self.r_power, 0.5)
		return r

	def _strength(self):
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
			apo_distance = Kerbin().r_a + body().r_a

			min_distance = min(peri_distance, apo_distance)
			max_distance = max(peri_distance, apo_distance)

		x_min = max(1 - (min_distance / self.signal_range), 0)
		x_max = max(1 - (max_distance / self.signal_range), 0)

		max_strength = -2 * pow(x_min,3) + 3 * pow(x_min,2)
		min_strength = -2 * pow(x_max, 3) + 3 * pow(x_max, 2)

		self.signal_strength = min_strength
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
		# a method to calculate the maximum theoretical distance between two satellites

		if sat_a.orbit.parent is sat_b.orbit.parent:
			# satallites of same body
			return (sat_a.orbit.r_a + sat_b.orbit.r_a)
		elif sat_a.orbit.parent().parent is sat_b.orbit.parent().parent:
			# satallites of bodies who share the same parent: Kerbin's moon and Duna's moon
			# max distance sum of the body's plus satellite's apoapsis
			return (sat_a.orbit.parent().r_a + sat_a.orbit.r_a) + (sat_b.orbit.parent().r_a + sat_b.orbit.r_a)
		elif sat_a.orbit.parent is sat_b.orbit.parent().parent:
			# sat_a is moon of body, sat_b is orbiting moon of body
			return (sat_a.orbit.r_a + sat_b.orbit.parent().r_a + sat_b.orbit.r_a)
		elif sat_a.orbit.parent().parent is sat_b.orbit.parent:
			# sat_b is moon of body, sat_a is orbiting moon of body
			return (sat_a.orbit.parent().r_a + sat_a.orbit.r_a + sat_b.orbit.r_a)
		else:
			print("SHOULD NOT GET HERE")


	def query_signal_strength(self, satellite, target_strength=0.7):
		visited = set()
		path, strength = self._find_signal_path(satellite, target_strength, visited)

		print(f"\n\x1b[1;36m{'=' * 60}")
		print(f"DNS Signal Path Strength Summary")
		print(f"{'=' * 60}\x1b[0m\n")

		print(f"\x1b[1;37mTarget Strength:\x1b[0m           \x1b[1;32m{round(target_strength*100)}%\x1b[0m")
		print(f"\x1b[1;37mFound Strength:\x1b[0m            \x1b[1;32m{round(strength*100)}%\x1b[0m\n")
		print(f"\x1b[1;36m{'-' * 60}\x1b[0m\n")		
	

	def _find_signal_path(self, me, target_strength, visited):
		if me in visited:
				return None, 0  # No path, no strength

		visited.add(me)

		# Check direct signal to DSN
		_, min_strength = me._strength()
		if min_strength > 0:
				return [me], min_strength

		best_path = None
		best_strength = 0

		for sat in self.satellites:
				if sat not in visited and sat.comm_type == 'Relay':
						signal_strength = self.signal_strength(me, sat)

						if signal_strength > 0:
								path, path_strength = self._find_signal_path(sat, target_strength, visited)

								if path:
										total_min_strength = min(signal_strength, path_strength)

										# Keep best overall even if under target_strength
										if total_min_strength > best_strength:
												best_path = [me] + path
												best_strength = total_min_strength

		# Either the best path over all children or None if nothing reachable
		return best_path, best_strength

	def signal_strength(self, sat, target):
		target_power = target.signal_power
		sat_range = sat.signal_range
		distance = self.max_distance_between(sat, target)

		x_max = 1 - (distance / sat_range)
		min_strength = -2 * pow(x_max, 3) + 3 * pow(x_max, 2)
		return min_strength	