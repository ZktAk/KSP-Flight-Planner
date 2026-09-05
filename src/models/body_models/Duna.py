from utils.body_registry import register_body, get_body
from models.body_models.Base_Class import CelestialBody
from utils.body_hierarchy import *
from utils.body_math_utils import *
import math

class Duna(CelestialBody):
  name = 'Duna'
  parent_name = parent_of[name]
  children_names = children_of[name]

  def __init__(self):
    super().__init__()
    parent = self.parent()

    # Physical properties
    self.radius = 320_000                       # m
    self.mass = 4.5154270E+21                   # kg
    self.mu = 3.0136321E+11                     # m^3/s^2
    self.g = self.mu / pow(self.radius, 2)      # m/s^2
    self.SOI = 47921949                         # m from center

    # Rotational properties
    self.rotation_period = 65517.859            # s, T_sid
    self.solar_day = 65766.707                  # s, T_sol
    self.rotation_speed = 30.688                # m/s

    # Atmospheric Properties
    self.atm_height = 50000                     # m
    self.standard_launch_height = 60_000        # m
    self.atm_delta_v = 430                     # m/s

    # Orbital parameters
    self.a = 20_726_155_264                     # m from center
    self.r_p = 19_669_121_365.3                 # m from center
    self.r_a = 21_783_189_162.7                 # m from center
    self.e = 0.051                              # unitless
    self.i = 0.06                               # °
    self.w = 0      #Argument of periapsis      # °
    self.RAAN = 135.5                           # °
    self.period = (2 * math.pi *                # s
                   pow(
                     pow(self.a, 3) /
                     parent.mu,
                     0.5)
                   )

    # Rotational properties
    # self.solar_day = 65766.707                  # s, T_sol
    # self.rotation_period = sol2sid(             # s, T_sid
    # 						 self.solar_day,
    # 						 self.period)
    # self.rotation_speed = 30.688                # m/s