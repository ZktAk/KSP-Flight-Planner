import math

from Bodies import *
import CommNet
import Antennas


class Orbit:
	def __init__(self, body, p_alt, a_alt, inc):
		self.body = body
		body = body()
		self.p_alt = p_alt
		self.a_alt = a_alt
		self.r_p = p_alt + body.radius
		self.r_a = a_alt + body.radius
		self.e = (self.r_a - self.r_p) / (self.r_a + self.r_p)
		self.a = self.r_a / (1 + self.e)
		self.h = self.a - body.radius
		self.i = inc
		self.T = 2 * math.pi * pow(pow(self.a,3)/body.mu,0.5)


class Maneuver:
	def __init__(self, type, description, delta_v):
		self.type = type
		self.name = description
		self.delta_v = delta_v


class Mission:
	def __init__(self, type="Custom", name="Unnamed Mission", origin=Kerbin):
		self.type = type
		self.name = name
		self.origin = self.current_body = origin
		self.launched = False
		self.aborted = False

		self.maneuvers = []
		self.orbits = []
		body = origin()
		self.orbits.append(Orbit(origin, body.radius, body.radius, 0))

	def _add_maneuver(self, type, description, delta_v):
		self.maneuvers.append(Maneuver(type, description, delta_v))
		self.type = "Custom"

	def _add_orbit(self, p_alt, a_alt, inc):
		self.orbits.append(Orbit(self.current_body, p_alt, a_alt, inc))

	def _catch(self, logic, severity, source, message, abort=False):
		if logic:
			severities = {'Warning': 'yellow', 'Error': 'orange', 'Failure': 'red'}
			color = {'Warning': '\x1b[1;34m', 'Error': '\x1b[1;33m', 'Failure': '\x1b[1;31m'}

			# print(f'\x1b[{'1;34'}m {"Warning"} \x1b[0m')
			# print(f'\x1b[{'1;33'}m {"Error"} \x1b[0m')
			# print(f'\x1b[{'1;31'}m {"Failure"} \x1b[0m')

			print(f'{color[severity]}{severity} in {source}\x1b[0m: {message}')
			if abort:
				self.aborted = True
			return True
		return False

	def _break_check(self, logic=False, severity=None, source=None, message=None, abort=False):
		if self.aborted: return True
		return self._catch(logic, severity, source, message, abort)

	def _valid_orbit(self, body=None, p_alt=None, a_alt=None, inc=None, source='<source not found>', param='<param not found>', atm_override=False):

		body = self.current_body() if body is None else body()

		defaults = [self.orbits[-1].p_alt, self.orbits[-1].a_alt, self.orbits[-1].i]
		values = [p_alt, a_alt, inc]
		p_alt, a_alt, inc = [v if v is not None else d for v, d in zip(values, defaults)]

		r_p = p_alt + body.radius
		r_a = a_alt + body.radius

		if self._catch(p_alt <= body.atm_height and not atm_override,
					   'Failure',
					   source,
					   f'{param} not greater than {body.name}\'s atmospheric height. Mission construction aborted!',
					   True):
			return False
		elif self._catch(p_alt <= body.atm_height and atm_override,
					   'Warning',
					   source,
					   f'{param} not greater than {body.name}\'s atmospheric height. \x1b[1;33m<Failure overridden>\x1b[0m. Maneuver added.',
					   False):
			pass

		elif self._catch(r_a >= body.SOI,
						 'Failure',
						 source,
						 f'{param} not less than {body.name}\'s sphere of influence. Mission construction aborted!',
						 True):
			return False

		elif self._catch(p_alt > a_alt,
							 'Failure',
							 source,
							 'Given periapsis is greater than apoapsis. Mission construction aborted!',
							 True):
			return False

		elif self._catch(not (0 <= inc < 360),
							   'Failure',
							   source,
							   'Given inclination invalid. Choose between 0 and 360. Mission construction aborted!',
							   True):
			return False

		elif self._catch(defaults == [p_alt, a_alt, inc],
						 'Error',
						 source,
						 'Requested orbit is identical to current orbit. No changes applied.'):
			return False


		for moon in body.children:
			moon = moon()
			inner_SOI = moon.r_p - moon.SOI
			outer_SOI = moon.r_a + moon.SOI
			logic = (inner_SOI <= r_p <= outer_SOI) or (inner_SOI <= r_a <= outer_SOI)
			self._catch(logic, 'Warning',
						source,
						f'{param} intersects {moon.name}\'s sphere of influence. Maneuver added.')

		return True

	def _Hohmann_transfer(self, final_Alt):
		# if self._break_check(self.orbits[-1].e != 0,
		#                      "Failure",
		#                      "_Hohmann_transfer()",
		#                      f'_Hohmann_transfer() requires initial orbit to be circular. '
		#                      f'Mission construction aborted!.',
		#                      True):
		# 	return

		body = self.current_body()
		mu = body.mu

		initial_Rad = self.orbits[-1].a
		final_Rad = body.radius + final_Alt
		a = (initial_Rad + final_Rad) / 2

		vis = pow(mu / initial_Rad, 0.5) * (pow(final_Rad / a, 0.5) - 1)
		viva = pow(mu / final_Rad, 0.5) * (1 - pow(initial_Rad / a, 0.5))
		delta_v = round(vis + viva, 1)

		return vis, viva, delta_v

	def _Coplanar_transfer(self, final_P_Alt, final_A_Alt):
		# if self._break_check(final_P_Alt > final_A_Alt,
		#                      'Failure',
		#                      '_Coplanar_transfer()',
		#                      'Given periapsis is greater than apoapsis. Mission construction aborted!',
		#                      True):
		# 	return

		body = self.current_body()
		R, mu = body.radius, body.mu

		# Starting orbit
		initial_P_Rad = self.orbits[-1].r_p
		initial_A_Rad = self.orbits[-1].r_a
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

	def _Inclination_change(self, new_inc):

		body = self.current_body()

		R, mu = body.radius, body.mu
		p_Rad = R + self.orbits[-1].p_alt
		a_Rad = R + self.orbits[-1].a_alt
		alpha = 2 / (a_Rad + p_Rad)
		a_Vol = pow(mu * (2 / a_Rad - alpha), 0.5)
		delta_i = new_inc - self.orbits[-1].i
		delta_v = round(a_Vol * pow(2 * (1 - math.cos(math.pi * delta_i / 180)), 0.5))
		return delta_v

	def Launch(self, alt=None, inc=0, Landing=False):

		# Error catching
		if self._break_check(self.launched,
						 'Error',
						 'Launch()',
						 f'Attempted to launch when already in orbit. Maneuver not added.'):
			return

		body = self.current_body()

		if self._catch(alt is None,
					   'Warning',
					   'Launch()',
					   f'Launch altitude not specified. Defaulting to standard {body.name} launch height of {body.standard_launch_height}m.'):
			alt = body.standard_launch_height

		if not self._valid_orbit(None, alt, alt, inc, 'Launch()', 'Launch altitude'):
			return

		# Computation

		R, mu, equatorial_Vol, drag_dv = (body.radius,
										  body.mu,
										  body.rotation_speed,
										  body.atm_delta_v)

		target_Rad = R + alt
		vis, viva, _ = self._Hohmann_transfer(target_Rad)

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

		if Landing:
			self._add_maneuver("Land",f"Controlled landing on {body.name}", delta_v)
			return
		self._add_maneuver("Launch",f"Launch from {body.name} to {alt}m circular orbit with {inc}° inclination", delta_v)
		self._add_orbit(alt, alt ,inc)
		self.launched = True

	def Land(self):
		body = self.current_body()
		if body.atm_height != 0:
			self.Change_Orbit(body.atm_height/2, self.orbits[-1].a_alt, atm_override=True)
			self._add_maneuver("Land", f"Aerobrake landing on {body.name}", 0)
			self.launched = False
		else:			
			# Error catching			
			alt = body.standard_launch_height
			inc = self.orbits[-1].i

			self.Change_Orbit(alt, alt, atm_override=True)
			
			self._add_orbit(body.radius, body.radius ,inc)
			self.launched = False
			self.Launch(body.standard_launch_height, inc, Landing=True)		

	def Change_Orbit(self, new_P_Alt=None, new_A_Alt=None, new_i=None, atm_override=False):
		# Error catching

		if self._break_check(new_P_Alt == new_A_Alt == new_i is None,
							 'Failure',
							 'Change_Orbit()',
							 f'No input received. Mission construction aborted!.',
							 True):
			return

		body = self.current_body()

		if self._catch(not self.launched,
					   'Failure',
					   'Change_Orbit()',
					   f'Cannot change orbit while still on surface of {body.name}. Mission construction aborted!.', True):
			return

		defaults = [self.orbits[-1].p_alt, self.orbits[-1].a_alt, self.orbits[-1].i]
		params = [new_P_Alt, new_A_Alt, new_i]
		params = [v if v is not None else d for v, d in zip(params, defaults)]
		new_P_Alt, new_A_Alt, new_i = params

		if not self._valid_orbit(None, new_P_Alt, new_A_Alt, new_i, 'Change_Orbit()', 'Orbit altitude', atm_override=atm_override):
			return

		description = ''

		if params[:2] != defaults[:2]:

			if (params[1] == defaults[1]) and (params[0] == defaults[1]):
				description = f'Circularization maneuver performed at A_alt = {new_A_Alt}m'
			else:
				n = 0
				for i in range(3):
					param = params[i]
					default = defaults[i]
					if param != default and n<2:
						separator = "" if n == 0 else " | "
						change = 'Increased' if param > default else 'Decreased'
						param_name = ['P_alt', 'A_Alt', 'Inclination'][i]
						unit = ['m', 'm', '°'][i]
						description += f'{separator}{change} {param_name} to {param}{unit}'
						n+=1

			self._add_maneuver("Coplanar Orbit Change", description, self._Coplanar_transfer(new_P_Alt, new_A_Alt))

		if new_i != self.orbits[-1].i:
			change = {True: 'Increased', False: 'Decreased'}[new_i > self.orbits[-1].i]
			description = f'{change} inclination to {new_i}°'
			self._add_maneuver("Mid-course Inclination Change", description, self._Inclination_change(new_i))

		self._add_orbit(new_P_Alt, new_A_Alt, new_i)

	def Transfer(self, target, final_P_Alt, final_A_Alt):
		current_body = self.current_body()
		target_body = target()
		logic = (target not in current_body.children) and (target is not current_body.parent)
		if self._break_check(logic, "Failure", "Transfer()",
							 f'Cannot transfer to {target_body.name} from {current_body.name}. Mission construction aborted!',
							 True):
			return

		if not self._valid_orbit(target, final_P_Alt, final_A_Alt, source='Transfer()', param='Orbit altitude', atm_override=True):
			return

		if self._catch(self.orbits[-1].e != 0, "Warning", "Transfer()",
					  f'Transfer orbit assumes initial orbit is circular. Added circularization maneuver to {self.orbits[-1].a_alt}m.'):
			self.Change_Orbit(self.orbits[-1].a_alt, self.orbits[-1].a_alt)

		initial_Alt = self.orbits[-1].a

		delta_v = None

		if target_body.parent is self.current_body:
			initial_Rad = current_body.radius + initial_Alt
			final_P_Rad = target_body.radius + final_P_Alt
			final_A_Rad = target_body.radius + final_A_Alt

			vis, viva, hohmann_v = self._Hohmann_transfer(target_body.a)
			transfer_cost = vis

			hyperbolic_v_p = pow(
				pow(viva, 2) - 2 * target_body.mu * (1 / target_body.SOI - 1 / final_P_Rad), 0.5)

			elliptical_v = pow(
				target_body.mu * (2 / final_P_Rad - 2 / (final_P_Rad + final_A_Rad)), 0.5)

			capture_cost = hyperbolic_v_p - elliptical_v
			delta_v = transfer_cost + capture_cost

			self._add_maneuver("Transfer",
								 f"Transfer from {current_body.name} to {target_body.name}",
												transfer_cost)
			self._add_orbit(self.orbits[-1].p_alt, target_body.a, self.orbits[-1].i)
			
	
			self._add_maneuver("Capture",
								 f"Capture into p_alt = {final_P_Alt}m, a_alt = {final_A_Alt}m orbit around {target_body.name}",
												capture_cost)
			self._add_orbit(final_P_Alt, final_A_Alt, self.orbits[-1].i)

		elif target is current_body.parent:
			initial_Rad = current_body.radius + initial_Alt
			final_P_Rad = target_body.radius + final_P_Alt

			v1 = pow(current_body.mu / initial_Rad, 0.5)
			a = (current_body.a + final_P_Rad) / 2
			v_a = pow(target_body.mu * (2 / current_body.a - 1 / a), 0.5)
			v = pow(target_body.mu / current_body.a, 0.5)
			leaving_v = v - v_a
			v_e = pow(pow(leaving_v, 2) + 2 * current_body.mu * (1 / initial_Rad - 1 / current_body.SOI), 0.5)

			delta_v = v_e - v1

			self._add_maneuver("Transfer and Capture",
								 f"Transfer from {current_body.name} to {target_body.name} and capture into p_alt = {final_P_Alt}m, a_alt = {final_A_Alt}m orbit.",
								 delta_v)
			self._add_orbit(final_P_Alt, final_A_Alt, self.orbits[-1].i)

		
		self.current_body = target

	def print_power_bill(self, power_usage):
		# power_usage in unit/s

		child = self.current_body
		orbit = self.orbits[-1]

		orbit_beta_deg = orbit.i
		orbit_alpha = math.acos(min(1, child().radius / orbit.a))
		orbit_eclipse_angle = 2 * orbit_alpha * math.cos(math.radians(orbit_beta_deg))
		orbit_eclipse_time = orbit_eclipse_angle * orbit.T / (2 * math.pi)

		parent_eclipse_time = 0

		if child().parent is not Kerbol:
			parent = child().parent
			parent_beta_deg = child().i
			parent_alpha = math.acos(min(1, parent().radius / child().a))
			parent_eclipse_angle = 2 * parent_alpha * math.cos(math.radians(parent_beta_deg))
			parent_eclipse_time = parent_eclipse_angle * child().period / (2 * math.pi)

		total_eclipse_time = orbit_eclipse_time + parent_eclipse_time
		sunlight_time = orbit.T - total_eclipse_time
		required_capacity = power_usage * total_eclipse_time

		print(f"\n\x1b[1;36m{'=' * 60}")
		print(f"Power Budget Summary for Mission: {self.name} ({self.type})")
		print(f"{'=' * 60}\x1b[0m")

		print(f"\x1b[1;37mOrbital Period:\x1b[0m                \x1b[1;32m{round(orbit.T):>10,} s\x1b[0m\n")
		print(f"\x1b[1;37mOrbital Eclipse Duration:\x1b[0m      \x1b[1;32m{round(orbit_eclipse_time):>10,} s\x1b[0m")
		print(
			f"\x1b[1;37mParent Eclipse Duration:\x1b[0m       \x1b[1;32m{round(parent_eclipse_time):>10,} s\x1b[0m\n")
		print(f"\x1b[1;37mTotal Time in Eclipse:\x1b[0m         \x1b[1;32m{round(total_eclipse_time):>10,} s\x1b[0m")
		print(f"\x1b[1;37mTotal Time in Sunlight:\x1b[0m        \x1b[1;32m{round(sunlight_time):>10,} s\x1b[0m\n")

		print(f"\x1b[1;36m{'-' * 60}")
		print(f"Required Battery Capacity:\t\t\t\x1b[1;32m{round(required_capacity):,} charge units\x1b[0m")
		print(f"\x1b[1;36m{'-' * 60}\x1b[0m\n")

		return required_capacity

	def print_maneuver_bill(self, surplus_percent=10):
		if self._break_check(not self.maneuvers,
		                     'Failure',
		                     'print_maneuver_bill()',
		                     f"No maneuvers recorded for mission: {self.name}",
		                     True):
			return


		print(f"\n\x1b[1;36m{'=' * 60}")
		print(f"Δv Budget Summary for Mission: {self.name} ({self.type})")
		print(f"{'=' * 60}\x1b[0m")

		total_dv = 0
		for i, m in enumerate(self.maneuvers, 1):
			print(f"\x1b[1;37mM{i}: {m.type:<20}\x1b[0m")
			print(f"    \x1b[0;36m{m.name}")
			print(f"    \x1b[1;32mΔv = {round(m.delta_v)} m/s\x1b[0m")
			print(f"    \x1b[1;32m+{surplus_percent}% = {round(m.delta_v*(1+surplus_percent/100))} m/s\x1b[0m\n")
			total_dv += m.delta_v

		print(f"\x1b[1;36m{'-' * 60}")
		print(f"Total Δv Requirement: {round(total_dv)} m/s\t|\tPlus {surplus_percent}%: {round(total_dv*(1+surplus_percent/100))}")
		print(f"{'-' * 60}\x1b[0m\n")

class Kerbin_orbitor(Mission):
	def __init__(self, alt=Kerbin().standard_launch_height, inc=0, type="Preset", name="Kerbin Orbitor", origin=Kerbin):
		super().__init__(type, name, origin)
		self.Launch(alt, inc)
		self.type = "Preset"

class Munar_orbitor(Mission):
	def __init__(self, target_p_alt=Mun().standard_launch_height, target_a_alt=Mun().standard_launch_height, inc=Mun().i, type="Preset", name="Munar Orbitor", origin=Kerbin):
		body = Mun
		super().__init__(type, name, origin)
		self.Launch(Kerbin().standard_launch_height, body().i)
		self.Transfer(body, target_p_alt, target_a_alt)
		self.Change_Orbit(target_p_alt, target_a_alt, inc)
		self.type = "Preset"

class Minmus_orbitor(Mission):
	def __init__(self, target_p_alt=Minmus().standard_launch_height, target_a_alt=Minmus().standard_launch_height, inc=Minmus().i, type="Preset", name="Minmus Orbitor", origin=Kerbin):
		body = Minmus
		super().__init__(type, name, origin)
		self.Launch(Kerbin().standard_launch_height, body().i)
		self.Transfer(body, target_p_alt, target_a_alt)
		self.Change_Orbit(target_p_alt, target_a_alt, inc)
		self.type = "Preset"
		
class Munar_lander(Munar_orbitor):
	def __init__(self, type="Preset", name="Mun Lander", origin=Kerbin):
		super().__init__(type=type, name=name, origin=origin)
		self.Land()
		self.type = "Preset"

class Minmus_lander(Minmus_orbitor):
	def __init__(self, type="Preset", name="Minmus Lander", origin=Kerbin):
		super().__init__(type=type, name=name, origin=origin)
		self.Land()
		self.type = "Preset"


if __name__ == "__main__":

	# Warning: Add maneuver
	# Error: Abort maneuver
	# Failure: Abort maneuver and mission

	#test1 = Minmus_lander()
	#test1.print_maneuver_bill(10)

	#test2 = Munar_orbitor()
	#test2.print_maneuver_bill(10)

	test3 = Kerbin_orbitor(450_000)
	test3.print_maneuver_bill(10)
	test3.print_power_bill(10)

	CommNet.Test_comms()
	# Antennas.Test_ants()
	
	
