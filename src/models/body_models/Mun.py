from utils.body_registry import register_body, get_body
from models.body_models.Base_Class import CelestialBody
from utils.body_hierarchy import *
from utils.body_math_utils import *
import math

class Mun(CelestialBody):
  name = 'The Mun'
  parent_name = parent_of[name]
  children_names = children_of[name]

  def __init__(self):
    super().__init__()
    parent = self.parent()

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