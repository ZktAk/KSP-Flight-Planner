import math

def time_in_eclipse(Beta, parent_radius, altitude, orbital_period):
	alpha = math.acos(parent_radius / (parent_radius + altitude))
	eclipse_angle = 2 * alpha * math.cos(Beta)
	return eclipse_angle * orbital_period / (2 * math.pi)

def time_in_sun(Beta, parent_radius, altitude, orbital_period):
	eclipse_time = time_in_eclipse(Beta, parent_radius, altitude, orbital_period)
	return orbital_period - eclipse_time

class Body:
	def __init__(self, name, parent_body, R, M, mu, T_sid, T_sol=None, SOI=1E+100, v_eq=0.0, atm_height=0, atm_dv=0,
	             a=None, r_a=None, r_p=None, e=0, i=0, w=0, W=0):

		self.name = name
		self.parent_body = parent_body
		self.radius = R
		self.mass = M
		self.mu = mu
		self.g = mu/pow(R,2)
		self.rotation_period = T_sid
		self.solar_day = T_sol
		self.SOI = SOI
		self.rotation_speed = v_eq
		self.Atmos_Height = atm_height
		self.Atmos_delta_v = atm_dv

		self.a = a
		self.r_p = r_p
		self.r_a = r_a
		self.e = e
		self.i = i
		self.w = w
		self.RAAN = W
		self.period = 2*math.pi*pow(pow(a,3)/parent_body.mu,0.5) if parent_body is not None else 0

# Planet definitions (unchanged)
Kerbol = Body("Kerbol", None, 261_600_000, 1.75655e+30, 1.17233e+18, 432000, atm_height=600_000)
Kerbin = Body("Kerbin", Kerbol, 600_000, 5.2915793e+22, 3.5316e+12, 21549, 21600, 83559000, 174.9, 70000, 1000, 13599840256, 13599840256, 13599840256)
Mun = Body("Mun", Kerbin, 200_000, 9.7600236e+20, 6.5138398e+10, 21756, None, 2429559.1, 57.8, 0, 0, 1.20e+07, 1.20e+07, 1.20e+07)
Minmus = Body("Minmus", Kerbin, 60_000, 2.6457897e+19, 1.7658e+09, 40400, None, 2247428.4, 9.3315, 0, 0, 4.70e+07, 4.70e+07, 4.70e+07, 0, 6, 38, 78)

Bodies = [Kerbol, Kerbin, Mun, Minmus]
bodies = {b.name: b for b in Bodies}

# class Kerbol:
# 	def __init__(self):
#
# 		# Physical properties
# 		self.radius = 261_600_000                   # m
# 		self.mass = 1.7565459E+28                      # kg
# 		self.mu = 1.1723328E+18                       # m^3/s^2
# 		self.g = self.mu / pow(self.radius, 2)      # why are you on the surface of the sun???
# 		self.SOI = float('inf')                     # m
#
# 		# Atmospheric Properties
# 		self.atm_height = 600_000                   # m
#
# class Kerbin():
# 	def __init__(self):
# 		self.parent = Kerbol
# 		parent = self.parent()
#
# 		# Physical properties
# 		self.radius = 600_000                       # m
# 		self.mass = 5.2915158E+22                   # kg
# 		self.mu = 3.5316000E+12                     # m^3/s^2
# 		self.g = self.mu / pow(self.radius, 2)      # m/s^2
# 		self.SOI = 84159286                         # m
#
# 		# Rotational properties
# 		self.rotation_period = 21549.425            # s, T_sid
# 		self.solar_day = 21600.000                  # s, T_sol
# 		self.rotation_speed = 174.94                # m/s
#
# 		# Atmospheric Properties
# 		self.atm_height = 70000                     # m
# 		self.atm_delta_v = 1000                     # m/s
#
# 		# Orbital parameters
# 		self.a = 13_599_840_256                     # m
# 		self.r_p = 13_599_840_256                   # m
# 		self.r_a = 13_599_840_256                   # m
# 		self.e = 0                                  # unitless
# 		self.i = 0                                  # °
# 		self.w = 0      #Argument of periapsis      # °
# 		self.RAAN = 0                               # °
# 		self.period = (2 * math.pi *                # s
# 		               pow(
# 			               pow(self.a, 3) /
# 			               parent.mu,
# 			               0.5)
# 		               )
#
# 		# Rotational properties
# 		self.solar_day = 21600.000                  # s, T_sol
# 		self.rotation_period = 1 / (                # s, T_sid
# 				(1 / self.solar_day) +
# 				(1 / self.period)
# 		)
# 		self.rotation_speed = 174.94                # m/s
#
# class Mun():
# 	def __init__(self):
# 		self.parent = Kerbin
# 		parent = self.parent()
#
# 		# Physical properties
# 		self.radius = 200_000                       # m
# 		self.mass = 9.7599066E+20                   # kg
# 		self.mu = 6.5138398E+10                     # m^3/s^2
# 		self.g = self.mu / pow(self.radius, 2)      # m/s^2
# 		self.SOI = 2429559.1                        # m from center
#
# 		# Atmospheric Properties
# 		self.atm_height = 0                         # m
# 		self.atm_delta_v = 0                        # m/s
#
# 		# Orbital parameters
# 		self.a = 12_000_000                         # m from center
# 		self.r_p = 12_000_000                       # m from center
# 		self.r_a = 12_000_000                       # m from center
# 		self.e = 0                                  # unitless
# 		self.i = 0                                  # °
# 		self.w = 0      #Argument of periapsis      # °
# 		self.RAAN = 0                               # °
# 		self.period = (2 * math.pi *                # s
# 		               pow(
# 			               pow(self.a, 3) /
# 			               parent.mu,
# 			               0.5)
# 		               )
# 		self.time_in_eclipse = time_in_eclipse(     # s
# 			self.i,
# 			parent.radius,
# 			self.r_p - parent.radius,
# 			self.period
# 		)
#
# 		# Rotational properties
# 		self.rotation_period = self.period          # s, T_sid, approx. 138_984.38 s
# 		self.solar_day = 1 / (                      # s, T_sol
# 				(1 / self.rotation_period)-
# 				(1 / parent.period)
# 		)
# 		self.rotation_speed = 9.0416                # m/s
#
# class Minmus():
# 	def __init__(self):
# 		self.parent = Kerbin
# 		parent = self.parent()
#
# 		# Physical properties
# 		self.radius = 60_000                        # m
# 		self.mass = 2.6457580E+19                   # kg
# 		self.mu = 1.7658000E+9                      # m^3/s^2
# 		self.g = self.mu / pow(self.radius, 2)      # m/s^2
# 		self.SOI = 2_247_428.4                      # m from center
#
# 		# Atmospheric Properties
# 		self.atm_height = 0                         # m
# 		self.atm_delta_v = 0                        # m/s
#
# 		# Orbital parameters
# 		self.a = 47_000_000                         # m from center
# 		self.r_p = 47_000_000                       # m from center
# 		self.r_a = 47_000_000                       # m from center
# 		self.e = 0                                  # unitless
# 		self.i = 6                                  # °
# 		self.w = 38      #Argument of periapsis     # °
# 		self.RAAN = 78                              # °
# 		self.period = (2 * math.pi *                # s
# 		               pow(
# 			               pow(self.a, 3) /
# 			               parent.mu,
# 			               0.5)
# 		               )
# 		self.time_in_eclipse = time_in_eclipse(     # s
# 			self.i,
# 			parent.radius,
# 			self.r_p - parent.radius,
# 			self.period
# 		)
#
# 		# Rotational properties
# 		self.rotation_period = 40400.000            # s, T_sid
# 		self.solar_day = 1 / (                      # s, T_sol
# 				(1 / self.rotation_period)-
# 				(1 / parent.period)
# 		)
# 		self.rotation_speed = 9.3315                # m/s
#
# 		# self.solar_day = 1220131.7  # s, T_sol
# 		# self.rotation_period = 1 / (  # s, T_sid
# 		# 		(1 / self.solar_day) +
# 		# 		(1 / parent.period)
# 		# )
# 		# self.rotation_speed = 174.94  # m/s
#
#
#
# # print(Kerbin().parent is Kerbol)
# # print(Kerbin().__class__ == Kerbin)
#
# mun = Minmus()
#
# print(mun.rotation_period)
# print(mun.period)
# print(mun.solar_day)
