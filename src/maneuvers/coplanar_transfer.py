def Coplanar_transfer(body, initial_P_Rad, initial_A_Rad, final_P_Alt, final_A_Alt):
  R, mu = body.radius, body.mu

  # Starting orbit
  alpha = 2 / (initial_A_Rad + initial_P_Rad)
  initial_P_Vol = pow(mu * (2 / initial_P_Rad - alpha), 0.5)
  initial_A_Vol = pow(mu * (2 / initial_A_Rad - alpha), 0.5)

  # Target orbit
  final_P_Rad = R + final_P_Alt
  final_A_Rad = R + final_A_Alt
  alpha = 2 / (final_A_Rad + final_P_Rad)
  final_P_Vol = pow(mu * (2 / final_P_Rad - alpha), 0.5)
  final_A_Vol = pow(mu * (2 / final_A_Rad - alpha), 0.5)

  # Transfer burn calculations
  if (final_P_Rad - initial_P_Rad) <= (final_A_Rad - initial_A_Rad):
    P_Rad = final_P_Rad
    A_Rad = initial_A_Rad
    alpha = 2 / (A_Rad + P_Rad)
    P_Vol = pow(mu * (2 / P_Rad - alpha), 0.5)
    A_Vol = pow(mu * (2 / A_Rad - alpha), 0.5)
    Burn1 = A_Vol - initial_A_Vol
    Burn2 = final_P_Vol - P_Vol
  else:
    P_Rad = initial_P_Rad
    A_Rad = final_A_Rad
    alpha = 2 / (A_Rad + P_Rad)
    P_Vol = pow(mu * (2 / P_Rad - alpha), 0.5)
    A_Vol = pow(mu * (2 / A_Rad - alpha), 0.5)
    Burn1 = P_Vol - initial_P_Vol
    Burn2 = final_A_Vol - A_Vol

  delta_v = abs(Burn1) + abs(Burn2)
  return delta_v	