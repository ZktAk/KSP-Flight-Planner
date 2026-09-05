def time_in_eclipse(Beta, parent_radius, altitude, orbital_period):
  import math
  alpha = math.acos(parent_radius / (parent_radius + altitude))
  eclipse_angle = 2 * alpha * math.cos(Beta)
  return eclipse_angle * orbital_period / (2 * math.pi)

def time_in_sun(Beta, parent_radius, altitude, orbital_period):
  eclipse_time = time_in_eclipse(Beta, parent_radius, altitude, orbital_period)
  return orbital_period - eclipse_time

def sol2sid(T_sol, T):
  return 1 / ((1 / T_sol) + (1 / T))

def sid2sol(T_sid, T):
  return 1 / ((1 / T_sid) - (1 / T))