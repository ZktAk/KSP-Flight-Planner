def Hohmann_transfer(initial_rad, final_rad, mu):
  a = (initial_rad + final_rad) / 2
  vis = pow(mu / initial_rad, 0.5) * (pow(final_rad / a, 0.5) - 1)
  viva = pow(mu / final_rad, 0.5) * (1 - pow(initial_rad / a, 0.5))
  delta_v = round(vis + viva, 1)
  return vis, viva, delta_v