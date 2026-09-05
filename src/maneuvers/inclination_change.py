def Inclination_change(initial_orbit, target_orbit):
  import math
  
  mu = initial_orbit.body().mu
  r_p = initial_orbit.r_p
  r_a = initial_orbit.r_a
  initial_i = initial_orbit.i
  new_i = target_orbit.i

  alpha = 2 / (r_a + r_p)
  a_Vol = pow(mu * (2 / r_a - alpha), 0.5)
  delta_i = new_i - initial_i
  delta_v = round(a_Vol * pow(2 * (1 - math.cos(math.pi * delta_i / 180)), 0.5))
  
  return delta_v