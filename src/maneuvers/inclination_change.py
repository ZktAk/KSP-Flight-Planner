def Inclination_change(body, r_p, r_a, initial_i, new_i):
  import math
  
  mu = body.mu
  alpha = 2 / (r_a + r_p)
  a_Vol = pow(mu * (2 / r_a - alpha), 0.5)
  delta_i = new_i - initial_i
  delta_v = round(a_Vol * pow(2 * (1 - math.cos(math.pi * delta_i / 180)), 0.5))
  
  return delta_v