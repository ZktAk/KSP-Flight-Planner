def launch(body, alt=None, inc=0, calculate_losses=False):
  """Estimate the launch delta-v needed to reach a circular orbit.

  The model uses a simplified ascent cost:
  - an ideal orbital speed at surface radius
  - a Hohmann transfer burn to reach the target altitude
  - an inclination/rotation adjustment from body spin
  - a fixed launch loss factor for drag and gravity losses
  - a final circularization burn at apoapsis
  """
  import math
  from maneuvers.hohmann_transfer import Hohmann_transfer
  
  # Body properties used for the launch calculation.
  R = body.radius
  mu = body.mu
  equatorial_rotation = body.rotation_speed

  if not calculate_losses:
    losses_dv = body.launch_loss_factor

  # Compute the two-part transfer from surface radius to orbit radius.
  # vis = burn at periapsis (surface) to raise apoapsis to target altitude.
  # viva = burn at apoapsis to circularize at the target orbit.
  vis, viva, _ = Hohmann_transfer(R, R + alt, mu)

  # Ideal circular orbital speed at the starting radius.
  orbital_speed = pow(mu / R, 0.5)

  # Base delta-v before accounting for planetary rotation/inclination.
  raw_dv = orbital_speed + vis

  # Account for launch inclination and equatorial rotation.
  # A prograde equatorial launch gets the full rotational boost.
  # Higher inclination launches lose more of that benefit.
  inc_rad = math.radians(inc)
  adjusted_dv = pow(raw_dv ** 2 + equatorial_rotation ** 2 -
                    (2 * raw_dv * equatorial_rotation * math.cos(inc_rad)), 0.5)

  # Total estimated launch cost, including drag/gravity losses and circularization.
  if not calculate_losses:
    delta_v = adjusted_dv + losses_dv + viva
    return delta_v
  else:
    delta_v = adjusted_dv + viva
    losses = body.average_launch_cost - delta_v
    losses = round((losses)/10) * 10
    return losses

  