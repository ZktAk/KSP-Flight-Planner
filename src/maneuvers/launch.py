def launch(body, alt=None, inc=0):
  import math
  from maneuvers.hohmann_transfer import Hohmann_transfer
  
  R = body.radius
  mu = body.mu
  equatorial_rotation = body.rotation_speed
  drag_dv = body.atm_delta_v

  vis, viva, _ = Hohmann_transfer(R, R + alt, mu)
  orbital_speed = pow(mu / R, 0.5)

  # Adjust for inclination and atmospheric drag
  raw_dv = orbital_speed + vis
  inc_rad = math.radians(inc)
  adjusted_dv = pow(raw_dv ** 2 + equatorial_rotation ** 2 -
                    (2 * raw_dv * equatorial_rotation * math.cos(inc_rad)), 0.5)
  delta_v = adjusted_dv + drag_dv + viva

  return delta_v