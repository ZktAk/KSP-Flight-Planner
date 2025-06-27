from utils.bodies import *
from models.orbit_model import Orbit
from maneuvers.launch import launch
from maneuvers.inclination_change import Inclination_change
from maneuvers.coplanar_transfer import Coplanar_transfer
from models.maneuver_model import Maneuver
import math
import warnings
from maneuvers.hohmann_transfer import Hohmann_transfer
from mission_error_catching import catch, break_check, valid_orbit

def pretty_ceil(num):
	return math.ceil(num/10)*10

class Mission:
	def __init__(self, type="Custom", name="Unnamed Mission", origin=Kerbin, building_preset=False, ignore_errors=None):
		self.type = type
		self.name = name
		self.origin = self.current_body = origin
		self.launched = False
		self.aborted = False
		self.ignore_errors = building_preset if ignore_errors is None else ignore_errors
		self.building_preset = building_preset

		self.maneuvers = []
		self.orbits = []
		body = origin()
		self.orbits.append(Orbit(origin, 0, 0, 0))

	def _finish_preset(self):
		self.building_preset = self.ignore_errors = False

	def _add_maneuver(self, type, description, delta_v):
		self.maneuvers.append(Maneuver(type, description, pretty_ceil(delta_v)))
		if not self.building_preset:
			self.type = "Custom"

	def _add_orbit(self, p_alt, a_alt, inc):
		self.orbits.append(Orbit(self.current_body, p_alt, a_alt, inc))

	def _Coplanar_transfer(self, final_P_Alt, final_A_Alt):
		return Coplanar_transfer(self.current_body(), self.orbits[-1].r_p, self.orbits[-1].r_a, final_P_Alt, final_A_Alt)		

	def _Inclination_change(self, new_inc):
		return Inclination_change(self.current_body(), self.orbits[-1].r_p, self.orbits[-1].r_a, self.orbits[-1].i, new_inc)

	def Launch(self, alt=None, inc=0, Landing=False):

		# Error catching
		if break_check(self, self.launched,
						 'Error',
						 'Launch()',
						 f'Attempted to launch when already in orbit. Maneuver not added.'):
			return

		body = self.current_body()

		if catch(self, alt is None,
					   'Warning',
					   'Launch()',
					   f'Launch altitude not specified. Defaulting to standard {body.name} launch height of {body.standard_launch_height:,}m.'):
			alt = body.standard_launch_height

		if not valid_orbit(self, None, alt, alt, inc, 'Launch()', 'Launch altitude'):
			return

		# Computation
		delta_v = launch(body, alt, inc)		

		# Add maneuver
		if Landing:
			self._add_maneuver("Land",f"Controlled landing on {body.name}", delta_v)
			return
		self._add_maneuver("Launch",f"Launch from {body.name} to {alt:,}m circular orbit with {inc}° inclination", delta_v)
		self._add_orbit(alt, alt ,inc)
		self.launched = True

	def Land(self):
		body = self.current_body()
		if body.atm_height != 0:
			self.Change_Orbit(body.atm_height/2, self.orbits[-1].a_alt, atm_override=True)
			self._add_maneuver("Land", f"Aerobrake landing on {body.name}", 0)
			self.orbits.append(Orbit(body, 0, 0, 0))
			self.launched = False
		else:			
			# Error catching			
			alt = body.standard_launch_height
			inc = self.orbits[-1].i

			self.Change_Orbit(alt, alt, atm_override=True)
			
			self._add_orbit(body.radius, body.radius ,inc)
			self.launched = False
			self.Launch(body.standard_launch_height, inc, Landing=True)
			self.orbits.append(Orbit(self.current_body, 0, 0, 0))


	def Change_Orbit(self, new_P_Alt=None, new_A_Alt=None, new_i=None, atm_override=False):
		# Error catching

		if break_check(self, new_P_Alt == new_A_Alt == new_i is None,
							 'Failure',
							 'Change_Orbit()',
							 f'No input received. Mission construction aborted!.',
							 True):
			return

		body = self.current_body()

		if catch(self, not self.launched,
					   'Failure',
					   'Change_Orbit()',
					   f'Cannot change orbit while still on surface of {body.name}. Mission construction aborted!.', True):
			return

		defaults = [self.orbits[-1].p_alt, self.orbits[-1].a_alt, self.orbits[-1].i]
		params = [new_P_Alt, new_A_Alt, new_i]
		params = [v if v is not None else d for v, d in zip(params, defaults)]
		new_P_Alt, new_A_Alt, new_i = params

		if not valid_orbit(self, None, new_P_Alt, new_A_Alt, new_i, 'Change_Orbit()', 'Orbit altitude', atm_override=atm_override):
			return

		description = ''

		if params[:2] != defaults[:2]:

			if (params[1] == defaults[1]) and (params[0] == defaults[1]):
				description = f'Circularization maneuver performed at A_alt = {new_A_Alt:,}m'
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
			self._add_orbit(new_P_Alt, new_A_Alt, self.orbits[-1].i)

		if new_i != self.orbits[-1].i:
			change = {True: 'Increased', False: 'Decreased'}[new_i > self.orbits[-1].i]
			description = f'{change} inclination to {new_i}°'
			self._add_maneuver("Mid-course Inclination Change", description, self._Inclination_change(new_i))
			self._add_orbit(new_P_Alt, new_A_Alt, new_i)

	def _transfer_cost(self, current_body, target_body, initial_Alt, target_p_alt):
		target = target_body.__class__
		child = current_body if target is current_body.parent else target_body
		parent = child.parent()
		parent_p_rad = parent.radius + target_p_alt if target is current_body.parent else self.orbits[-1].a
		parent_a_rad = current_body.a if target is current_body.parent else child.a
		child_alt = initial_Alt if target is current_body.parent else target_p_alt

		vis, v2, _ = Hohmann_transfer(parent_p_rad, parent_a_rad, parent.mu)

		if child.name == "Duna":
			print(f'\nr1: {parent_p_rad:,} m')
			print(f'r2: {parent_a_rad:,} m')
			print(f'mu: {round(parent.mu/1_000_000_000_000):,} * 10^12')
			print(f'Kerbin.mu: {round(Kerbin().mu/1_000_000_000)/1000:,}')
			print(f'\nvis: {round(vis)} m/s')
			print(f'v2: {round(v2)} m/s')

		r1 = child.radius + child_alt
		r2 = round(child.SOI / 1000) * 1000

		mu = child.mu
		v_e = round(pow(pow(v2, 2) + (2 * mu * (1 / r1 - 1 / r2)), 0.5))
		v = round(pow(mu / r1, 0.5))
		delta_v = v_e - v

		return vis, delta_v

	def Transfer(self, target, target_p_alt, target_a_alt=None):
		target_a_alt = target_p_alt if target_a_alt is None else target_a_alt
		current_body = self.current_body()
		target_body = target()
		logic = (target not in current_body.children) and (target is not current_body.parent) and (target_body.parent is not current_body.parent)
		if break_check(self, logic, "Failure", "Transfer()",
							 f'Cannot transfer to {target_body.name} from {current_body.name}. Mission construction aborted!',
							 True):
			return

		if not valid_orbit(self, target, target_p_alt, target_a_alt, source='Transfer()', param='Orbit altitude', atm_override=True):
			return

		if catch(self, self.orbits[-1].e != 0, "Warning", "Transfer()",
					  f'Transfer orbit assumes initial orbit is circular. Added circularization maneuver to {self.orbits[-1].a_alt:,}m.'):
			self.Change_Orbit(self.orbits[-1].a_alt, self.orbits[-1].a_alt)

		initial_Alt = self.orbits[-1].a_alt

		if target_body.parent is self.current_body:
			transfer, capture = self._transfer_cost(current_body, target_body, initial_Alt, target_p_alt)

			self._add_maneuver("Transfer",
								 f"Transfer from {current_body.name} to {target_body.name}", transfer)
			self._add_orbit(self.orbits[-1].p_alt, target_body.a, self.orbits[-1].i)

			if target_body.i != self.orbits[-1].i:
				change = {True: 'Increased', False: 'Decreased'}[target_body.i > self.orbits[-1].i]
				description = f'{change} inclination to {target_body.i}°'
				self._add_maneuver("Mid-course Inclination Change", description, self._Inclination_change(target_body.i))
				self._add_orbit(self.orbits[-1].p_alt, target_body.a, target_body.i)

			self._add_maneuver("Capture",
								 f"Capture into {target_p_alt:,}m circular orbit around {target_body.name}",
												capture)

		elif target is current_body.parent:
			transfer, delta_v = self._transfer_cost(current_body, target_body, initial_Alt, target_p_alt)

			self._add_maneuver("Transfer and Capture",
								 f"Transfer from {current_body.name} to {target_body.name} and capture into {target_p_alt:,}m circular orbit.",
								 delta_v)

		elif target_body.parent is current_body.parent:
			ejection_speed, encounter_speed, _ = Hohmann_transfer(current_body.a, target_body.r_a, target().parent.mu)
			# print(f'\nejection_speed: {round(ejection_speed)} m/s')
			# print(f'capture_speed: {round(encounter_speed)} m/s')

			mu = target().parent.mu
			viva = pow(mu / target_body.r_p, 0.5) * (pow(target_body.r_a / target_body.a, 0.5) - 1)
			# print(f'viva: {round(viva)} m/s')
			encounter_speed -= viva
			# print(f'capture_speed: {round(encounter_speed)} m/s')

			mu = current_body.mu
			r1 = self.orbits[-1].a
			r2 = current_body.SOI
			v2 = ejection_speed
			v1 = pow(2*mu*(1/r1 - 1/r2) + pow(v2,2),0.5)
			#print(v1)
			v = pow(mu/r1,0.5)
			#print(v)
			ejection_burn = v1 - v
			#print(f'\nejection_burn: {round(ejection_burn)} m/s')

			self._add_maneuver("Ejection Burn",
			                   f"Ejection out of {current_body.name}'s SOI on course to intercept {target_body.name}", ejection_burn)
			self.current_body = target().parent
			self._add_orbit(current_body.a, target_body.r_a, self.orbits[-1].i)

			mu = target().mu
			r1 = target().radius + target_p_alt
			r2 = target().SOI
			v2 = encounter_speed
			v1 = pow(2 * mu * (1 / r1 - 1 / r2) + pow(v2, 2), 0.5)
			#print(v1)
			v = pow(mu/r1, 0.5)
			#print(v)
			capture_burn = v1 - v
			#(f'capture_burn: {round(capture_burn)} m/s')

			self._add_maneuver("Capture Burn",
			                   f"Capture into {target_p_alt:,}m circular orbit around {target_body.name}",
			                   capture_burn)

		self.current_body = target
		self._add_orbit(target_p_alt, target_a_alt, self.orbits[-1].i)

	def print_power_bill(self, power_usage):
		# power_usage in unit/s
		orbit = self.orbits[-1]
		body = self.current_body()
		

		beta = orbit.i
		alpha = math.acos(body.radius / orbit.a)
		eclipse_angle = 2 * alpha * math.cos(math.radians(beta))
		eclipse_time = eclipse_angle * orbit.T / (2 * math.pi)

		moon_eclipse_time = 0

		if body.parent is not Kerbol:
			moon = body
			planet = moon.parent()
			
			beta = moon.i
			alpha = math.acos(planet.radius / moon.a)
			eclipse_angle = math.pi - (2 * alpha * math.cos(math.radians(beta)))
			moon_eclipse_time = eclipse_angle * moon.period / (2 * math.pi)

		total_eclipse_time = eclipse_time + moon_eclipse_time
		sunlight_time = orbit.T - total_eclipse_time
		required_capacity = power_usage * total_eclipse_time

		print(f"\n\x1b[1;36m{'=' * 60}")
		print(f"Power Budget Summary for Mission: {self.name} ({self.type})")
		print(f"{'=' * 60}\x1b[0m")

		print(f"\x1b[1;37mOrbital Period:\x1b[0m                \x1b[1;32m{round(orbit.T):>10,} s\x1b[0m\n")
		print(f"\x1b[1;37mOrbital Eclipse Duration:\x1b[0m      \x1b[1;32m{round(eclipse_time):>10,} s\x1b[0m")
		print(
			f"\x1b[1;37mParent Eclipse Duration:\x1b[0m       \x1b[1;32m{round(moon_eclipse_time):>10,} s\x1b[0m\n")
		print(f"\x1b[1;37mTotal Time in Eclipse:\x1b[0m         \x1b[1;32m{round(total_eclipse_time):>10,} s\x1b[0m")
		print(f"\x1b[1;37mTotal Time in Sunlight:\x1b[0m        \x1b[1;32m{round(sunlight_time):>10,} s\x1b[0m\n")

		print(f"\x1b[1;36m{'-' * 60}")
		print(f"Required Battery Capacity:\t\t\t\x1b[1;32m{round(required_capacity):,} charge units\x1b[0m")
		print(f"\x1b[1;36m{'-' * 60}\x1b[0m\n")
		return round(required_capacity)

	def print_maneuver_bill(self):
		if break_check(self, not self.maneuvers,
		                     'Failure',
		                     'print_maneuver_bill()',
		                     f"No maneuvers recorded for mission: {self.name}",
		                     True):
			return

		print(f"\n\x1b[1;36m{'=' * 60}")
		print(f"Δv Budget Summary for Mission: {self.name} ({self.type})")
		print(f"{'=' * 60}\x1b[0m")

		total_dv = 0
		total_surplus = 0
		for i, m in enumerate(self.maneuvers, 1):			
			surplus_percent = 25 if m.type =="Land" else 10
			total_surplus += pretty_ceil(m.delta_v*(1+surplus_percent/100))
			print(f"\x1b[1;37mM{i}: {m.type:<20}\x1b[0m")
			print(f"    \x1b[0;36m{m.name}")
			print(f"    \x1b[1;32mΔv = {m.delta_v} m/s\x1b[0m")
			print(f"    \x1b[1;32m+{surplus_percent}% = {pretty_ceil(m.delta_v*(1+surplus_percent/100))} m/s\x1b[0m\n")
			total_dv += m.delta_v

		print(f"\x1b[1;36m{'-' * 60}")
		print(f"Minimum Δv Requirement: {total_dv} m/s\t|\tPlus Margin : {total_surplus} m/s")
		print(f"{'-' * 60}\x1b[0m\n")

	def complete(self):
		return self.orbits[-1]