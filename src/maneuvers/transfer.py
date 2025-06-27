def _transfer_cost(current_body, target_body, initial_Alt, target_p_alt):
  from maneuvers.hohmann_transfer import Hohmann_transfer
  
  target = target_body.__class__
  child = current_body if target is current_body.parent else target_body
  parent = child.parent()
  parent_p_rad = parent.radius + target_p_alt if target is current_body.parent else self.orbits[-1].a
  parent_a_rad = current_body.a if target is current_body.parent else child.a
  child_alt = initial_Alt if target is current_body.parent else target_p_alt

  vis, v2, _ = Hohmann_transfer(parent_p_rad, parent_a_rad, parent.mu)
  r1 = child.radius + child_alt
  r2 = round(child.SOI / 1000) * 1000

  mu = child.mu
  v_e = round(pow(pow(v2, 2) + (2 * mu * (1 / r1 - 1 / r2)), 0.5))
  v = round(pow(mu / r1, 0.5))
  delta_v = v_e - v

  return vis, delta_v

def _transfer_to_child(current_body, target_body, initial_Alt, initial_i, target_i, target_p_alt):
  transfer, capture = _transfer_cost(current_body, target_body, initial_Alt, target_p_alt)

  maneuver1 = ["Transfer",
               f"Transfer from {current_body.name} to {target_body.name}", 
               transfer]
  orbit1 = [self.orbits[-1].p_alt, target_body.a, initial_i]

  if target_i != initial_i:
    change = {True: 'Increased', False: 'Decreased'}[target_i > initial_i]
    description = f'{change} inclination to {target_i}°'
    self._add_maneuver("Mid-course Inclination Change", description, self._Inclination_change(target_i))
    self._add_orbit(self.orbits[-1].p_alt, target_body.a, target_i)

  return maneuver1, orbit1
  

def Transfer(self, current, target, initial_Alt, initial_i, target_i, target_p_alt, target_a_alt=None):
  target_a_alt = target_p_alt if target_a_alt is None else target_a_alt
  current_body = current()
  target_body = target()

  if target_body.parent is current:
    transfer, capture = _transfer_cost(current_body, target_body, initial_Alt, initial_i, target_i, target_p_alt)

    self._add_maneuver("Transfer",
               f"Transfer from {current_body.name} to {target_body.name}", transfer)
    self._add_orbit(self.orbits[-1].p_alt, target_body.a, initial_i)

    if target_body.i != self.orbits[-1].i:
      change = {True: 'Increased', False: 'Decreased'}[target_body.i > self.orbits[-1].i]
      description = f'{change} inclination to {target_body.i}°'
      self._add_maneuver("Mid-course Inclination Change", description, self._Inclination_change(target_body.i))
      self._add_orbit(self.orbits[-1].p_alt, target_body.a, target_body.i)

    self._add_maneuver("Capture",
               f"Capture into {target_p_alt:,}m circular orbit around {target_body.name}",
                      capture)

  elif target is current_body.parent:
    transfer, delta_v = self._transfer_cost(current_body, target_body, initial_Alt, target_p_alt)

    self._add_maneuver("Transfer and Capture",
               f"Transfer from {current_body.name} to {target_body.name} and capture into {target_p_alt:,}m circular orbit.",
               delta_v)

  elif target_body.parent is current_body.parent:
    ejection_speed, encounter_speed, _ = Hohmann_transfer(current_body.a, target_body.r_a, target().parent.mu)
    # print(f'\nejection_speed: {round(ejection_speed)} m/s')
    # print(f'capture_speed: {round(encounter_speed)} m/s')

    mu = target().parent.mu
    viva = pow(mu / target_body.r_p, 0.5) * (pow(target_body.r_a / target_body.a, 0.5) - 1)
    # print(f'viva: {round(viva)} m/s')
    encounter_speed -= viva
    # print(f'capture_speed: {round(encounter_speed)} m/s')

    mu = current_body.mu
    r1 = self.orbits[-1].a
    r2 = current_body.SOI
    v2 = ejection_speed
    v1 = pow(2*mu*(1/r1 - 1/r2) + pow(v2,2),0.5)
    #print(v1)
    v = pow(mu/r1,0.5)
    #print(v)
    ejection_burn = v1 - v
    #print(f'\nejection_burn: {round(ejection_burn)} m/s')

    self._add_maneuver("Ejection Burn",
                       f"Ejection out of {current_body.name}'s SOI on course to intercept {target_body.name}", ejection_burn)
    self.current_body = target().parent
    self._add_orbit(current_body.a, target_body.r_a, self.orbits[-1].i)

    mu = target().mu
    r1 = target().radius + target_p_alt
    r2 = target().SOI
    v2 = encounter_speed
    v1 = pow(2 * mu * (1 / r1 - 1 / r2) + pow(v2, 2), 0.5)
    #print(v1)
    v = pow(mu/r1, 0.5)
    #print(v)
    capture_burn = v1 - v
    #(f'capture_burn: {round(capture_burn)} m/s')

    self._add_maneuver("Capture Burn",
                       f"Capture into {target_p_alt:,}m circular orbit around {target_body.name}",
                       capture_burn)

  self.current_body = target
  self._add_orbit(target_p_alt, target_a_alt, self.orbits[-1].i)