from Missions import * 

class Kerbin_orbitor(Mission):
  def __init__(self, alt=Kerbin().standard_launch_height, inc=0, type="Preset", name="Kerbin Orbitor", origin=Kerbin, building_preset=False):
    super().__init__(type, name, origin)
    self.Launch(alt, inc)
    if not building_preset: self._finish_preset()

class Munar_orbitor(Mission):
  def __init__(self, target_p_alt=Mun().standard_launch_height, target_a_alt=Mun().standard_launch_height, inc=Mun().i, type="Preset", name="Munar Orbitor", origin=Kerbin, building_preset=False):
    body = Mun
    super().__init__(type, name, origin, building_preset=True)
    self.Launch(Kerbin().standard_launch_height, body().i)
    self.Transfer(body, target_p_alt, target_a_alt)
    self.Change_Orbit(target_p_alt, target_a_alt, inc)
    if not building_preset: self._finish_preset()

class Minmus_orbitor(Mission):
  def __init__(self, target_p_alt=Minmus().standard_launch_height, target_a_alt=Minmus().standard_launch_height, inc=Minmus().i, type="Preset", name="Minmus Orbitor", origin=Kerbin, building_preset=False):
    body = Minmus
    super().__init__(type, name, origin, building_preset=True)
    self.Launch(Kerbin().standard_launch_height, body().i)
    self.Transfer(body, target_p_alt, target_a_alt)
    self.Change_Orbit(target_p_alt, target_a_alt, inc)
    if not building_preset: self._finish_preset()

class Munar_lander(Munar_orbitor):
  def __init__(self, type="Preset", name="Mun Lander", origin=Kerbin, building_preset=False):
    super().__init__(type=type, name=name, origin=origin)
    self.Land()
    if not building_preset: self._finish_preset()

class Minmus_lander(Minmus_orbitor):
  def __init__(self, type="Preset", name="Minmus Lander", origin=Kerbin, building_preset=False):
    super().__init__(type=type, name=name, origin=origin, building_preset=True)
    self.Land()
    if not building_preset: self._finish_preset()

class Duna_launch(Mission):
  def __init__(self, alt=Duna().standard_launch_height, inc=0, type="Preset", name="Duna Orbitor", origin=Duna, building_preset=False):
    super().__init__(type, name, origin)
    self.Launch(alt, inc)
    if not building_preset: self._finish_preset()

class Duna_transfer(Mission):
  def __init__(self, target_p_alt=Duna().standard_launch_height, target_a_alt=Duna().standard_launch_height, inc=Duna().i, type="Preset", name="Duna Orb", origin=Kerbin, building_preset=False):
    super().__init__(type, name, origin)
    self.Launch(Kerbin().standard_launch_height, 0)
    self.Transfer(Duna, target_p_alt)
    if not building_preset: self._finish_preset()
    #self.Transfer(Kerbol, Kerbin().r_p-Kerbol().radius)
    #self.Transfer(Mun, Mun().standard_launch_height)
    #self.Transfer(Minmus, Minmus().standard_launch_height)
