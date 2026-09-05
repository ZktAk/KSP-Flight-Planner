from utils.body_registry import register_body, get_body
from models.body_models.Base_Class import CelestialBody
from utils.body_hierarchy import *
from utils.body_math_utils import *
import math

class Kerbin(CelestialBody):
  name = 'Kerbin'
  parent_name = parent_of[name]
  children_names = children_of[name]
  
  def __init__(self):
    super().__init__()
    parent = self.parent()

    # Physical properties
    self.radius = 600_000                       # m
    self.mass = 5.2915158E+22                   # kg
    self.mu = 3.5316000E+12                     # m^3/s^2
    self.g = self.mu / pow(self.radius, 2)      # m/s^2
    self.SOI = 84_159_286                       # m from center

    # Rotational properties
    self.rotation_period = 21549.425            # s, T_sid
    self.solar_day = 21600.000                  # s, T_sol
    self.rotation_speed = 174.94                # m/s

    # Atmospheric Properties
    self.atm_height = 70000                     # m
    self.standard_launch_height = 80_000        # m
    self.atm_delta_v = 1000                     # m/s

    # Orbital parameters
    self.a = 13_599_840_256                     # m from center
    self.r_p = 13_599_840_256                   # m from center
    self.r_a = 13_599_840_256                   # m from center
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