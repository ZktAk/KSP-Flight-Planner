from utils.body_registry import register_body, get_body
from models.body_models.Base_Class import CelestialBody
from utils.body_hierarchy import *
from utils.body_math_utils import *
import math


class Moho(CelestialBody):
	name = 'Moho'
	parent_name = parent_of[name]
	children_names = children_of[name]
	
	def __init__(self):
		super().__init__()
		parent = self.parent()
		
		# Physical properties
		self.radius = 250_000  # m
		self.mass = 2.5263314E+21  # kg
		self.mu = 1.6860938E+11  # m^3/s^2
		self.g = self.mu / pow(self.radius, 2)  # m/s^2
		self.SOI = 9_646_663  # m from center
		
		# Rotational properties
		self.rotation_period = 1_210_000.0  # s, T_sid
		self.solar_day = 2_665_723.4  # s, T_sol
		self.rotation_speed = 1.2982  # m/s
		
		# Atmospheric Properties
		self.atm_height = 0  # m
		self.standard_launch_height = 20_000  # m
		self.atm_delta_v = 0  # m/s
		
		# Orbital parameters
		self.a = 5_263_138_304  # m from center
		self.r_p = 4_210_510_627.5  # m from center
		self.r_a = 6_315_765_980.5  # m from center
		self.e = 0.2  # unitless
		self.i = 7  # °
		self.w = 15  # Argument of periapsis      # °
		self.RAAN = 70  # °
		self.period = (2 * math.pi *  # s
		               pow(
			               pow(self.a, 3) /
			               parent.mu,
			               0.5)
		               )
		
		# # Rotational properties
		# self.solar_day = 21600.000  # s, T_sol
		# self.rotation_period = sol2sid(  # s, T_sid
		# 	self.solar_day,
		# 	self.period)
		# self.rotation_speed = 174.94  # m/s