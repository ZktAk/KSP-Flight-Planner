from Bodies import *
#from colorama import init
#from termcolor import colored
#init()

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

# mission methods

def transfer_to(self, target, final_P_Alt, final_A_Alt):
	logic = (target not in self.current_body.children) and (target is not self.current_body.parent)
	if self._break_check(logic, "Failure", "transfer_to()", f'Cannot transfer to {target.name} from {self.current_body.name}. Mission construction aborted!', True):
		return

	if self.catch(self.orbits[-1].r_p != self.orbits[-1].r_a, "Warning", "transfer_to()", f'Transfer orbit assumes initial orbit is circular. Added circularization maneuver to {self.orbits[-1].r_a}m.'):
		self.add_change_orbit(self.orbits[-1].r_a, self.orbits[-1].r_a, self.orbits[-1].i)

	# Refactor self.add_change_orbit to defualt to current inclinationn if none is specified

	initial_Body = self.current_body()
	target_Body = target()
	initial_Alt = self.orbits[-1].a

	if self.current_body is target_Body.parent:
		initial_Rad = initial_Body.radius + initial_Alt
		final_P_Rad = target_Body.radius + final_P_Alt
		final_A_Rad = target_Body.radius + final_A_Alt

		vis, viva, hohmann_v = self.hohmann_transfer(target_Body().a)
		transfer = vis
		
		hyperbolic_v_p = pow(
			pow(viva, 2) - 2 * target_Body.mu * (1 / target_Body.SOI - 1 / final_P_Rad), 0.5)

		elliptical_v = pow(
			target_Body.mu * (2 / final_P_Rad - 2 / (final_P_Rad + final_A_Rad)), 0.5)
		
		capture_cost = hyperbolic_v_p - elliptical_v
		delta_v = self.transfer_cost + self.capture_cost
		
	elif target is self.current_body().parent:
		initial_Rad = initial_Body.radius + initial_Alt
		final_P_Rad = target_Body.radius + final_P_Alt

		v1 = pow(initial_Body.mu / initial_Rad, 0.5)
		a = (initial_Body.a + final_P_Rad) / 2
		v_a = pow(target_Body.mu * (2 / initial_Body.a - 1 / a), 0.5)
		v = pow(target_Body.mu / initial_Body.a, 0.5)
		leaving_v = v - v_a
		v_e = pow(pow(leaving_v, 2) + 2 * initial_Body.mu * (1 / initial_Rad - 1 / initial_Body.SOI), 0.5)

		delta_v = v_e - v1

	
class LKO(mission):
	def __init__(self, mission_name="Low Kerbin Orbit", starting_body=Kerbin):
		super().__init__(mission_name, starting_body)
		self.add_launch(80_000)

class Low_Minmus_Orbit(mission):
	def __init__(self, mission_name="Low Minmus Orbit", starting_body=Kerbin):
		super().__init__(mission_name, starting_body)
		self.add_launch(80_000)
		self.add_transfer(Minmus, 14_000, 14_000)


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


# class Mission:
# 	def __init__(self, mission_name="Unnamed Mission", starting_body="Kerbin"):
# 		self.name = mission_name
# 		self.start = self.current_body = starting_body
# 		self.launched = False
# 		self.orbits = []
# 		self.manuevers = []
# 		self.descriptions = []
#
# 	def add_change_orbit(self, new_P_Alt=None, new_A_Alt=None, new_i=None, p=True):
# 		if not self.launched:
# 			print("[ERROR] Cannot change orbit before launch.")
# 			return
#
# 		current = self.orbits[-1]
# 		new_i = current.i if new_i is None else new_i
# 		new_P_Alt = current.p_alt if new_P_Alt is None else new_P_Alt
# 		new_A_Alt = current.a_alt if new_A_Alt is None else new_A_Alt
#
# 		self.manuevers.append(Coplanar_transfer(bodies[self.current_body],
# 												current.p_alt,
# 												current.a_alt,
# 												new_P_Alt,
# 												new_A_Alt))
# 		self.descriptions.append(f"Change orbit to Hp={new_P_Alt} m, Ha={new_A_Alt} m")
#
# 		if new_i != current.i:
# 			self.manuevers.append(Inclination_burn(bodies[self.current_body],
# 												   new_P_Alt,
# 												   new_A_Alt,
# 												   current.i,
# 												   new_i))
# 			self.descriptions.append(f"Change inclination from {current.i}° to {new_i}°")
#
# 		if p:
# 			print(f'Success: Changed orbit to \n\tHp = {new_P_Alt}m, \n\tHa = {new_A_Alt}m, \n\ti = {new_i}°.')
#
# 		self.orbits.append(Orbit(bodies[self.current_body], new_P_Alt, new_A_Alt, new_i))
#
# 	def add_transfer(self, target_Body, final_P_Alt, final_A_Alt, p=True):
# 		current_orbit = self.orbits[-1]
# 		if current_orbit.p_alt != current_orbit.a_alt:
# 			self.add_change_orbit(current_orbit.p_alt, current_orbit.p_alt, p=False)
# 			if p:
# 				print(f'Warning: Transfer orbit assumes initial orbit is circular. '
# 					  f'Added circularization maneuver to {current_orbit.p_alt}m.')
#
# 		self.manuevers.append(Transfer_and_capture(bodies[self.current_body],
# 												   bodies[target_Body],
# 												   current_orbit.p_alt,
# 												   final_P_Alt,
# 												   final_A_Alt))
# 		self.orbits.append(Orbit(bodies[target_Body], final_P_Alt, final_A_Alt, 0))
# 		self.current_body = target_Body
#
# 		self.descriptions.append(f"Transfer to {target_Body} orbit: Hp={final_P_Alt} m, Ha={final_A_Alt} m")
# 		if p:
# 			print(f'Success: Added transfer to Hp = {final_P_Alt}m x Ha = {final_A_Alt}m orbit around {target_Body}.')
#
# 	def add_land(self, p=True):
# 		current_orbit = self.orbits[-1]
# 		if current_orbit.p_alt != current_orbit.a_alt:
# 			self.add_change_orbit(current_orbit.p_alt, current_orbit.p_alt, p=False)
# 			if p:
# 				print(f'Warning: Landing maneuver assumes initial orbit is circular. '
# 					  f'Added circularization maneuver to {current_orbit.p_alt}m.')
#
# 		self.manuevers.append(Launch(bodies[self.current_body], current_orbit.p_alt, 0))  # Placeholder
# 		self.descriptions.append(f"Descent to surface of {self.current_body} from {current_orbit.p_alt} m orbit")
# 		if p:
# 			print(f'Success: Added landing maneuver to surface of {self.current_body}.')
#
# 	def add_return_home(self, p=True):
# 		if self.current_body == "Kerbin":
# 			reentry_apoapsis = self.orbits[-1].a_alt
# 		else:
# 			reentry_apoapsis = bodies[self.current_body].a
#
# 		# Insert return header and placeholder for delta-v (0 m/s)
# 		self.descriptions.append("<Initiating Return Home>")
# 		self.manuevers.append(None)  # Keep indices aligned; handled explicitly in print_BOD()
#
# 		maneuver = Transfer_and_capture(bodies[self.current_body],
# 										bodies["Kerbin"],
# 										self.orbits[-1].p_alt,
# 										30_000,
# 										reentry_apoapsis)
#
# 		self.manuevers.append(maneuver)
# 		self.descriptions.append(f"Return to Kerbin: Hp=30,000 m, Ha={reentry_apoapsis} m")
#
# 		self.orbits.append(Orbit(bodies["Kerbin"], 30_000, reentry_apoapsis, 0))
# 		self.current_body = "Kerbin"
# 		self.launched = False
#
# 		if p:
# 			print(f'Success: Added return trajectory to Kerbin atmosphere (30,000m periapsis).')
#
# 	def print_BOD(self):
# 		print(f"\n========== BILL OF DELTA-V — {self.name} ==========\n")
# 		print(f"{'Δv (m/s)':<10} | Maneuver Description")
# 		print(f"{'-' * 60}")
# 		total = 0
#
# 		for desc, maneuver in zip(self.descriptions, self.manuevers):
# 			if desc == "<Initiating Return Home>":
# 				print(f"\n<<<<<< Initiating Return to Kerbin >>>>>>\n")
# 				continue
#
# 			dv = maneuver.delta_v if maneuver else 0
# 			total += dv
# 			print(f"{dv:<10.1f} | {desc}")
#
# 		print(f"\n{'-' * 60}")
# 		print(f"{'TOTAL Δv:':<20} {round(total)} m/s")
# 		print(f"{'With 10% Margin:':<20} {round(total * 1.1)} m/s")
# 		print(f"{'=' * 60}\n")


# Example usage
if __name__ == "__main__":
	# Mission1 = Mission("Munar Round Trip")
	# Mission1.add_launch(80_000)
	# Mission1.add_transfer("Mun", 14_000, 14_000)
	# #Mission1.add_transfer("Kerbin", 30_000, bodies["Kerbin"].a)
	# Mission1.add_return_home()
	# Mission1.print_BOD()

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
