from src.models.orbit_model import Orbit
from src.utils.import_bodies import *


def _speed_at_periapsis_flyby(body, periapsis, speed_at_SOI):
    r1 = periapsis
    r2 = body().SOI
    mu = body().mu
    v2 = speed_at_SOI
    
    v1 = pow(pow(v2, 2) + (2 * mu * (1/r1 - 1/r2)), 0.5)
    return v1

def eliptical_v(mu, r, a):
    return pow(mu*(2/r - 1/a),0.5)

def circular_v(mu, r):
    return eliptical_v(mu, r, r)

def _transfer_to_child(parent_orbit, child_orbit):
    from src.maneuvers.hohmann_transfer import Hohmann_transfer
    from src.maneuvers.inclination_change import Inclination_change
    r1 = parent_orbit.a
    r2 = child_orbit.body().r_a
    
    mu = parent_orbit.body().mu
    transfer_delta_v, entry_speed, _ = Hohmann_transfer(r1, r2, mu)
    flyby_speed = _speed_at_periapsis_flyby(child_orbit.body, child_orbit.r_p, entry_speed)
    
    transfer_orbit = Orbit(parent_orbit.body, r1, r2, parent_orbit.i)
    inclined_transfer_orbit = Orbit(parent_orbit.body, r1, r2, child_orbit.body().i)
    inclination_delta_v = Inclination_change(transfer_orbit, inclined_transfer_orbit)
    
    return transfer_delta_v, flyby_speed, inclination_delta_v
    

def _transfer_and_capture_to_child(parent_orbit, child_orbit):
    transfer_delta_v, flyby_speed, inclination_delta_v = _transfer_to_child(parent_orbit, child_orbit)
    
    final_orbit_v = eliptical_v(child_orbit.body().mu, child_orbit.r_p, child_orbit.a)
    capture_delta_v = flyby_speed - final_orbit_v
    return transfer_delta_v, inclination_delta_v, capture_delta_v
    
    
def _transfer_to_parent(parent_orbit, child_orbit):
    transfer_delta_v, inclination_delta_v, capture_delta_v = _transfer_and_capture_to_child(parent_orbit, child_orbit)
    return capture_delta_v, 0, 0

def _transfer_and_capture_to_parent(parent_orbit, child_orbit):
    transfer_delta_v, inclination_delta_v, capture_delta_v = _transfer_and_capture_to_child(parent_orbit, child_orbit)
    return capture_delta_v, transfer_delta_v

def _transfer_and_capture_to_sibling(original_orbit, target_orbit=None):
    from src.maneuvers.hohmann_transfer import Hohmann_transfer
    
    original_body = original_orbit.body()
    target_body = target_orbit.body()
    parent_body = original_body.parent()

    origin_exit_speed, target_enter_speed_partial, _ = Hohmann_transfer(original_body.a, target_body.a, parent_body.mu)
    #print(origin_exit_speed)
    
    origin_flyby_speed = _speed_at_periapsis_flyby(original_orbit.body, original_orbit.r_p, origin_exit_speed)
    origin_orbit_speed = eliptical_v(original_body.mu, original_orbit.r_p, original_orbit.a)
    ejection_delta_v = origin_flyby_speed - origin_orbit_speed
    print(ejection_delta_v)
    
    vis, _, _ =  Hohmann_transfer(target_body.a, target_body.a, parent_body.mu)
    target_enter_speed = target_enter_speed_partial - vis
    #print(target_enter_speed)

    target_flyby_speed = _speed_at_periapsis_flyby(target_orbit.body, target_orbit.r_p, target_enter_speed)
    target_orbit_speed = eliptical_v(target_body.mu, target_orbit.r_p, target_orbit.a)
    capture_delta_v = target_flyby_speed - target_orbit_speed
    print(capture_delta_v)
    
    return ejection_delta_v, capture_delta_v


    
    
    
if __name__ == "__main__":

    orbit_1 = Orbit(Kerbin, 80_000, 80_000, 0)
    orbit_2 = Orbit(Moho, 20_000, 20_000, 0)

    
    _transfer_and_capture_to_sibling(orbit_1, orbit_2)
    
    
    



# def Transfer(initial_orbit, target_orbit):
#     from src.models.orbit_model import Orbit
#     initial_body_type = initial_orbit.body
#     initial_body = initial_body_type()
#     initial_r_p = initial_orbit.r_p
#     initial_r_a = initial_orbit.r_a
#
#     target_body_type = target_orbit.body
#     target_body = target_body_type()
#     target_r_p = target_orbit.r_p
#     target_r_a = target_orbit.r_a
#
#
#     if initial_body_type is target_body.parent:  # always "if A is B's parent"
#         transfer, capture = _transfer_cost(initial_orbit, target_orbit)
#
#
# def transfer(self, target, target_p_alt, target_a_alt=None):
#
#     if target_body.parent is self.current_body:
#         transfer, capture = self._transfer_cost(current_body, target_body, initial_Alt, target_p_alt)
#
#         self._add_maneuver("Transfer",
#                            f"Transfer from {current_body.name} to {target_body.name}", transfer)
#         self._add_orbit(self.orbits[-1].p_alt, target_body.a, self.orbits[-1].i)
#
#         if target_body.i != self.orbits[-1].i:
#             change = {True: 'Increased', False: 'Decreased'}[target_body.i > self.orbits[-1].i]
#             description = f'{change} inclination to {target_body.i}°'
#             self._add_maneuver("Mid-course Inclination Change", description, self._Inclination_change(target_body.i))
#             self._add_orbit(self.orbits[-1].p_alt, target_body.a, target_body.i)
#
#         self._add_maneuver("Capture",
#                            f"Capture into {target_p_alt:,}m circular orbit around {target_body.name}",
#                            capture)
#
#     elif target is current_body.parent:
#         transfer, delta_v = self._transfer_cost(current_body, target_body, initial_Alt, target_p_alt)
#
#         self._add_maneuver("Transfer and Capture",
#                            f"Transfer from {current_body.name} to {target_body.name} and capture into {target_p_alt:,}m circular orbit.",
#                            delta_v)
#
#     elif target_body.parent is current_body.parent:
#         ejection_speed, encounter_speed, _ = Hohmann_transfer(current_body.a, target_body.r_a, target().parent.mu)
#         # print(f'\nejection_speed: {round(ejection_speed)} m/s')
#         # print(f'capture_speed: {round(encounter_speed)} m/s')
#
#         mu = target().parent.mu
#         viva = pow(mu / target_body.r_p, 0.5) * (pow(target_body.r_a / target_body.a, 0.5) - 1)
#         # print(f'viva: {round(viva)} m/s')
#         encounter_speed -= viva
#         # print(f'capture_speed: {round(encounter_speed)} m/s')
#
#         mu = current_body.mu
#         r1 = self.orbits[-1].a
#         r2 = current_body.SOI
#         v2 = ejection_speed
#         v1 = pow(2 * mu * (1 / r1 - 1 / r2) + pow(v2, 2), 0.5)
#         # print(v1)
#         v = pow(mu / r1, 0.5)
#         # print(v)
#         ejection_burn = v1 - v
#         # print(f'\nejection_burn: {round(ejection_burn)} m/s')
#
#         self._add_maneuver("Ejection Burn",
#                            f"Ejection out of {current_body.name}'s SOI on course to intercept {target_body.name}",
#                            ejection_burn)
#         self.current_body = target().parent
#         self._add_orbit(current_body.a, target_body.r_a, self.orbits[-1].i)
#
#         mu = target().mu
#         r1 = target().radius + target_p_alt
#         r2 = target().SOI
#         v2 = encounter_speed
#         v1 = pow(2 * mu * (1 / r1 - 1 / r2) + pow(v2, 2), 0.5)
#         # print(v1)
#         v = pow(mu / r1, 0.5)
#         # print(v)
#         capture_burn = v1 - v
#         # (f'capture_burn: {round(capture_burn)} m/s')
#
#         self._add_maneuver("Capture Burn",
#                            f"Capture into {target_p_alt:,}m circular orbit around {target_body.name}",
#                            capture_burn)
#
#     self.current_body = target
#     self._add_orbit(target_p_alt, target_a_alt, self.orbits[-1].i)