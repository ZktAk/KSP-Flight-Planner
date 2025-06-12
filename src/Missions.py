from Bodies import *

def catch(logic, message, abort=False):
	if logic:
		print(message)
	return abort


class Orbit:
	def __init__(self, body, p_alt, a_alt, inc):
		self.body = body
		self.p_alt = p_alt
		self.a_alt = a_alt
		self.i = inc


class Maneuver:
	def __init__(self, name, delta_v):
		self.name = name
		self.delta_v = delta_v


class mission:
	def __init__(self, type="Custom", name="Unnamed Mission", origin=Kerbin):
		self.type = type
		self.name = name
		self.origin = self.current_body_class = origin
		self.launched = False
		self.aborted = False

		self.Maneuvers = []
		self.Orbits = []

	def _add_maneuver(self, name, delta_v):
		self.Maneuvers.append(Maneuver(name, delta_v))

	def _add_orbit(self, p_alt, a_alt, inc):
		self.Maneuvers.append(Orbit(self.current_body_class, p_alt, a_alt, inc))


	def _catch(self, logic, severity, source, message, abort=False):
		if logic:
			severities = {'Warning': 'yellow', 'Error': 'orange', 'Failure': 'red'}
			print(f'{severity} in {source}: {message}')
			if abort:
				self.aborted = True
			return True
		return False


	def _break_check(self, logic, severity, source, message, abort=False):
		if self.aborted: return True
		return self._catch(logic, severity, source, message, abort)


	def _Hohmann_transfer(self, initial_Alt, final_Alt):
		body = self.current_body_class()
		mu = body.mu
		initial_Rad = body.radius + initial_Alt
		final_Rad = body.radius + final_Alt
		a = (initial_Rad + final_Rad) / 2

		vis = pow(mu / initial_Rad, 0.5) * (pow(final_Rad / a, 0.5) - 1)
		viva = pow(mu / final_Rad, 0.5) * (1 - pow(initial_Rad / a, 0.5))
		delta_v = round(vis + viva, 1)

		return vis, viva, delta_v


	def Launch(self, alt=None, inc=0):

		# Error catching

		if self._break_check(self.launched, 'Error', 'Launch()', f'Attempted to launch when already in orbit. Maneuver not added.'):
			return

		body = self.current_body_class()

		if self._catch(alt is None, 'Warning', 'Launch()', f'Launch altitude not specified. Defaulting to {body.standard_launch_height}m.'):
			alt = body.standard_launch_height
		#elif self._catch(alt <= body.atm_height, f'Failure in Launch(): Launch height not greater than {body.name}\'s atmospheric height. Mission construction aborted!', True):
			#return
		#elif self._catch(alt >= body.SOI, f'Failure in Launch(): Launch height not less than {body.name}\'s sphere of influence. Mission construction aborted!', True):
			#return
		for moon in body.children:
			moon = moon()
			inner_SOI = moon.r_p - moon.SOI
			outer_SOI = moon.r_a + moon.SOI
			logic = inner_SOI <= alt <= outer_SOI
			#self._catch(logic, f'Warning in Launch(): Launch altitude intersects {moon.name}\'s sphere of influence. Maneuver added.')


		# Computation

		R, mu, equatorial_Vol, drag_dv = (body.radius,
		                                  body.mu,
		                                  body.rotation_speed,
		                                  body.atm_delta_v)

		target_Rad = R + alt
		vis, viva, _ = self._Hohmann_transfer(R, target_Rad)

		equatorial_orbit_V = pow(mu / R, 0.5)

		# At launch, we must first get up to the required speed for a theoretical circular orbit of altitude 0m.
		# Assuming that our position once we accomplish this is at periphrasis (just for the sake of nomenclature
		# though since ideally we are in a circular arbit), we then need to add to that the required delta-v to raise
		# our apoapsis to our target_Alt. This is or course idealized in that we assume the first delta-v to circular
		# equatorial orbit is instantaneous and that our acceleration vector during which is pointed parallel to the
		# surface. This is error is reduced by later adding a drag delta-v factor to account for atmospheric drag losses
		# during ascent.
		ascension_dv = equatorial_orbit_V + vis

		# Here we adjust the ascension_dv factor according to the influence of the equatorial rotation velocity which depends on
		# the inclination of ascent.
		adjusted_ascension_dv = pow(pow(ascension_dv, 2) + pow(equatorial_Vol, 2) - (
					2 * ascension_dv * equatorial_Vol * math.cos(math.pi * inc / 180)), 0.5)

		# Here we add on that drag delta-v factor as well as the delta-v required to circularize.
		delta_v = round((adjusted_ascension_dv + drag_dv + viva) / 10) * 10

		self._add_maneuver(f"Launch from {body.name} to {alt}m circular orbit", delta_v)
		self._add_orbit(alt, alt ,inc)
		self.launched = True


	def Change_Orbit(self, new_P_Alt=None, new_A_Alt=None, new_i=None):
		# Error catching

		if self._break_check(new_P_Alt == new_A_Alt == new_i is None, 'Failure in Change_Orbit(): No input received. Mission construction aborted!.', True):
			return

		body = self.current_body_class()

		if self._catch(not self.launched, f'Failure in Change_Orbit(): Cannot change orbit while still on surface of {body.name}. Mission construction aborted!.', True):
			return

# Example usage
if __name__ == "__main__":

	# Warning: Add maneuver
	# Error: Abort maneuver
	# Failure: Abort maneuver and mission

	test = mission()
	#print(Mun().a-Kerbin().radius)
	#test.Launch(11400000)
	test.Launch(80_000)
	test.Launch(50_000)
	#test.Launch()
	#test.Change_Orbit(1)
