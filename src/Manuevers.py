# Manuevers.py
import math
from Bodies import Kerbin, Mun, Minmus


class Hohmann_transfer:
	def __init__(self, body, initial_Alt, final_Alt):
		self.name = f"Hohmann Transfer around {body.name}: {initial_Alt}m → {final_Alt}m"

		mu = body.mu
		initial_Rad = body.radius + initial_Alt
		final_Rad = body.radius + final_Alt
		a = (initial_Rad + final_Rad) / 2
		self.vis = pow(mu / initial_Rad, 0.5) * (pow(final_Rad / a, 0.5) - 1)
		self.viva = pow(mu / final_Rad, 0.5) * (1 - pow(initial_Rad / a, 0.5))
		self.delta_v = round(self.vis + self.viva, 1)


class Coplanar_transfer:
	def __init__(self, body, initial_P_Alt, initial_A_Alt, final_P_Alt, final_A_Alt):
		self.name = f"Coplanar Transfer around {body.name}: {initial_P_Alt}m x {initial_A_Alt}m → {final_P_Alt}m x {final_A_Alt}m"

		R, mu = body.radius, body.mu

		# Starting orbit
		initial_P_Rad = R + initial_P_Alt
		initial_A_Rad = R + initial_A_Alt
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

		self.delta_v = round(abs(Burn1) + abs(Burn2), 1)


class Launch:

	def __init__(self, body, target_Alt=80_000, target_inclination=0):
		self.name = f"Launch from {body.name} to {target_Alt}m @ {target_inclination}°"

		R, mu, equatorial_Vol, drag_dv = body.radius, body.mu, body.rotation_speed, body.Atmos_delta_v

		target_Rad = R + target_Alt
		self.Hohmann = Hohmann_transfer(body, R, target_Rad)
		vis_dv = self.Hohmann.vis
		viva_dv = self.Hohmann.viva

		equatorial_orbit_V = pow(mu/R, 0.5)

		# at launch, we must first get up to the required speed for a theoretical circular orbit of altitude 0m.
		# assuming that our position once we accomplish this is at periphrasis (just for the sake of nomenclature
		# though since ideally we are in a circular arbit), we then need to add to that the required delta-v to raise
		# our apoapsis to our target_Alt. This is or course idealized in that we assume the first delta-v to circular
		# equatorial orbit is instantaneous and that our acceleration vector during which is pointed parallel to the
		# surface. This is error is reduced by later adding a drag delta-v factor to account for atmospheric drag losses
		# during ascent.
		ascension_dv = equatorial_orbit_V + vis_dv

		# here we adjust the ascension_dv factor according to the influence of the equatorial rotation velocity which depends on
		# the inclination of ascent.
		adjusted_ascension_dv = pow(pow(ascension_dv, 2) + pow(equatorial_Vol, 2) - (2 * ascension_dv * equatorial_Vol * math.cos(math.pi * target_inclination / 180)), 0.5)

		# here we add on that drag delta-v factor as well as the delta-v required to circularize.
		self.delta_v = round((adjusted_ascension_dv + drag_dv + viva_dv)/10)*10


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


class Transfer_and_capture:
	def __init__(self, initial_Body, target_Body, initial_Alt, final_P_Alt, final_A_Alt):
		if initial_Body is target_Body.parent_body:
			self.name = f"Transfer from {initial_Body.name} to {target_Body.name}"

			initial_Rad = initial_Body.radius + initial_Alt
			final_P_Rad = target_Body.radius + final_P_Alt
			final_A_Rad = target_Body.radius + final_A_Alt

			self.Hohmann = Hohmann_transfer(initial_Body, initial_Rad, target_Body.a)

			transfer = self.Hohmann.vis
			self.transfer_cost = round(transfer / 10) * 10

			viva = self.Hohmann.viva
			hyperbolic_v_p = pow(
				pow(viva, 2) - 2 * target_Body.mu * (1 / target_Body.SOI - 1 / final_P_Rad), 0.5)

			elliptical_v = pow(
				target_Body.mu * (2 / final_P_Rad - 2 / (final_P_Rad + final_A_Rad)), 0.5)

			self.capture_cost = round((hyperbolic_v_p - elliptical_v) / 10) * 10
			self.delta_v = self.transfer_cost + self.capture_cost

		elif target_Body is initial_Body.parent_body:
			self.name = f"Transfer and capture from circular {initial_Alt}m around {initial_Body.name} to elliptical {final_P_Alt}m (periapsis) around {target_Body.name}"

			initial_Rad = initial_Body.radius + initial_Alt
			final_P_Rad = target_Body.radius + final_P_Alt

			v1 = pow(initial_Body.mu / initial_Rad, 0.5)
			a = (initial_Body.a + final_P_Rad) / 2
			v_a = pow(target_Body.mu * (2 / initial_Body.a - 1 / a), 0.5)
			v = pow(target_Body.mu / initial_Body.a, 0.5)
			leaving_v = v - v_a
			v_e = pow(pow(leaving_v, 2) + 2 * initial_Body.mu * (1 / initial_Rad - 1 / initial_Body.SOI), 0.5)

			self.delta_v = round(v_e - v1)

		else:
			self.name = f"Transfer from {initial_Body.name} to {target_Body.name}"
			self.delta_v = 0
			print("Cannot directly transfer from Body 1 to Body 2")
