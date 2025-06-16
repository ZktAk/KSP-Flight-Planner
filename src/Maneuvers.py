# Manuevers.py
import math
from Bodies import Kerbin, Mun, Minmus

class Inclination_burn:
	def __init__(self, body, p_Alt, a_Alt, initial_inclination, final_inclination):
		self.name = f"Inclination Change at {p_Alt}m by {a_Alt}m: {initial_inclination}° → {final_inclination}°"

		R, mu = body.radius, body.mu
		p_Rad = R + p_Alt
		a_Rad = R + a_Alt
		alpha = 2 / (a_Rad + p_Rad)
		a_Vol = pow(mu * (2 / a_Rad - alpha), 0.5)
		delta_i = final_inclination - initial_inclination
		self.delta_v = round(a_Vol * pow(2 * (1 - math.cos(math.pi * delta_i / 180)), 0.5))


class RAAN_burn(Inclination_burn):
	pass

