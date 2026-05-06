from utils.body_registry import register_body, get_body
from models.body_models.Base_Class import CelestialBody
from utils.body_hierarchy import *



class Kerbol(CelestialBody):
  name = 'Kerbol'
  children_names = children_of[name]
  
  def __init__(self):
    super().__init__()
    
    # Physical properties
    self.radius = 261_600_000                   # m
    self.mass = 1.7565459E+28                   # kg
    self.mu = 1.1723328E+18                     # m^3/s^2
    self.g = self.mu / pow(self.radius, 2)      # why are you on the surface of the sun???
    self.SOI = float('inf')                     # m

    # Atmospheric Properties
    self.atm_height = 600_000                   # m

  @classmethod
  def _parent(cls): 
    return None