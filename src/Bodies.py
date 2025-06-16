import math

def time_in_eclipse(Beta, parent_radius, altitude, orbital_period):
	alpha = math.acos(parent_radius / (parent_radius + altitude))
	eclipse_angle = 2 * alpha * math.cos(Beta)
	return eclipse_angle * orbital_period / (2 * math.pi)

def time_in_sun(Beta, parent_radius, altitude, orbital_period):
	eclipse_time = time_in_eclipse(Beta, parent_radius, altitude, orbital_period)
	return orbital_period - eclipse_time

def sol2sid(T_sol, T):
	return 1 / ((1 / T_sol) + (1 / T))

def sid2sol(T_sid, T):
	return 1 / ((1 / T_sid) - (1 / T))

class Kerbol:
	def __init__(self):
		self.children = [Kerbin]

		# Physical properties
		self.radius = 261_600_000                   # m
		self.mass = 1.7565459E+28                   # kg
		self.mu = 1.1723328E+18                     # m^3/s^2
		self.g = self.mu / pow(self.radius, 2)      # why are you on the surface of the sun???
		self.SOI = float('inf')                     # m

		# Atmospheric Properties
		self.atm_height = 600_000                   # m

class Kerbin():
	def __init__(self):
		self.parent = Kerbol
		parent = self.parent()
		self.name = "Kerbin"
		self.children = [Mun, Minmus]

		# Physical properties
		self.radius = 600_000                       # m
		self.mass = 5.2915158E+22                   # kg
		self.mu = 3.5316000E+12                     # m^3/s^2
		self.g = self.mu / pow(self.radius, 2)      # m/s^2
		self.SOI = 84159286                         # m

		# Rotational properties
		self.rotation_period = 21549.425            # s, T_sid
		self.solar_day = 21600.000                  # s, T_sol
		self.rotation_speed = 174.94                # m/s

		# Atmospheric Properties
		self.atm_height = 70000                     # m
		self.standard_launch_height =80_000        # m
		self.atm_delta_v = 1000                     # m/s

		# Orbital parameters
		self.a = 13_599_840_256                     # m
		self.r_p = 13_599_840_256                   # m
		self.r_a = 13_599_840_256                   # m
		self.e = 0                                  # unitless
		self.i = 0                                  # °
		self.w = 0      #Argument of periapsis      # °
		self.RAAN = 0                               # °
		self.period = (2 * math.pi *                # s
		               pow(
			               pow(self.a, 3) /
			               parent.mu,
			               0.5)
		               )

		# Rotational properties
		self.solar_day = 21600.000                  # s, T_sol
		self.rotation_period = sol2sid(             # s, T_sid
							   self.solar_day,
							   self.period)
		self.rotation_speed = 174.94                # m/s

class Mun():
	def __init__(self):
		self.parent = Kerbin
		parent = self.parent()
		self.name = "The Mun"
		self.children = []

		# Physical properties
		self.radius = 200_000                       # m
		self.mass = 9.7599066E+20                   # kg
		self.mu = 6.5138398E+10                     # m^3/s^2
		self.g = self.mu / pow(self.radius, 2)      # m/s^2
		self.SOI = 2429559.1                        # m from center

		# Atmospheric Properties
		self.atm_height = 0                         # m
		self.standard_launch_height = 14_000        # m
		self.atm_delta_v = 0                        # m/s

		# Orbital parameters
		self.a = 12_000_000                         # m from center
		self.r_p = 12_000_000                       # m from center
		self.r_a = 12_000_000                       # m from center
		self.e = 0                                  # unitless
		self.i = 0                                  # °
		self.w = 0      #Argument of periapsis      # °
		self.RAAN = 0                               # °
		self.period = (2 * math.pi *                # s
		               pow(
			               pow(self.a, 3) /
			               parent.mu,
			               0.5)
		               )
		self.time_in_eclipse = time_in_eclipse(     # s
			self.i,
			parent.radius,
			self.r_p - parent.radius,
			self.period
		)

		# Rotational properties
		self.rotation_period = self.period          # s, T_sid, approx. 138_984.38 s
		self.solar_day = sid2sol(                   # s, T_sol
						 self.rotation_period,
						 parent.period)
		self.rotation_speed = 9.0416                # m/s

class Minmus():
	def __init__(self):
		self.parent = Kerbin
		parent = self.parent()
		self.name = "Minmus"
		self.children = []

		# Physical properties
		self.radius = 60_000                        # m
		self.mass = 2.6457580E+19                   # kg
		self.mu = 1.7658000E+9                      # m^3/s^2
		self.g = self.mu / pow(self.radius, 2)      # m/s^2
		self.SOI = 2_247_428.4                      # m from center

		# Atmospheric Properties
		self.atm_height = 0                         # m
		self.standard_launch_height = 10_000        # m
		self.atm_delta_v = 0                        # m/s

		# Orbital parameters
		self.a = 47_000_000                         # m from center
		self.r_p = 47_000_000                       # m from center
		self.r_a = 47_000_000                       # m from center
		self.e = 0                                  # unitless
		self.i = 6                                  # °
		self.w = 38      #Argument of periapsis     # °
		self.RAAN = 78                              # °
		self.period = (2 * math.pi *                # s
		               pow(
			               pow(self.a, 3) /
			               parent.mu,
			               0.5)
		               )
		self.time_in_eclipse = time_in_eclipse(     # s
			self.i,
			parent.radius,
			self.r_p - parent.radius,
			self.period
		)

		# Rotational properties
		self.rotation_period = 40400.000            # s, T_sid
		self.solar_day = sid2sol(                   # s, T_sol
						 self.rotation_period,
						 parent.period)
		self.rotation_speed = 9.3315                # m/s

# Example usage
if __name__ == "__main__":
	# print(Kerbin().parent is Kerbol)
	# print(Kerbin().__class__ == Kerbin)

	mun = Kerbin()

	print(mun.rotation_period)
	print(mun.solar_day)
	print(mun.period)
