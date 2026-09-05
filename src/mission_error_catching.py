def catch(mission_instance, logic, severity, source, message, abort=False):
  self = mission_instance
  if logic:
    severities = {'Warning': 'yellow', 'Error': 'orange', 'Failure': 'red'}
    color = {'Warning': '\x1b[1;34m', 'Error': '\x1b[1;33m', 'Failure': '\x1b[1;31m'}

    # Warning: Add maneuver
    # Error: Abort maneuver
    # Failure: Abort maneuver and mission

    # print(f'\x1b[{'1;34'}m {"Warning"} \x1b[0m')
    # print(f'\x1b[{'1;33'}m {"Error"} \x1b[0m')
    # print(f'\x1b[{'1;31'}m {"Failure"} \x1b[0m')

    if self.ignore_errors and severity != 'Failure': return False
    #raise Warning(f'{color[severity]}{severity} in {source}\x1b[0m: {message}')  # this line is only for development debugging and should be removed for production
    print(f'{color[severity]}{severity} in {source}\x1b[0m: {message}')
    if abort:
      self.aborted = True
    return True
  return False

def break_check(mission_instance, logic=False, severity=None, source=None, message=None, abort=False):
  self = mission_instance
  if self.aborted: return True
  return catch(self, logic, severity, source, message, abort)

def valid_orbit(mission_instance, body=None, p_alt=None, a_alt=None, inc=None, source='<source not found>', param='<param not found>', atm_override=False):
  self = mission_instance
  body = self.current_body() if body is None else body()

  defaults = [self.orbits[-1].p_alt, self.orbits[-1].a_alt, self.orbits[-1].i]
  values = [p_alt, a_alt, inc]
  p_alt, a_alt, inc = [v if v is not None else d for v, d in zip(values, defaults)]

  r_p = p_alt + body.radius
  r_a = a_alt + body.radius

  if catch(self, p_alt <= body.atm_height and not atm_override,
           'Failure',
           source,
           f'{param} not greater than {body.name}\'s atmospheric height. Mission construction aborted!',
           True):
    return False
  elif catch(self, p_alt <= body.atm_height and atm_override,
           'Warning',
           source,
           f'{param} not greater than {body.name}\'s atmospheric height. \x1b[1;33m<Failure overridden>\x1b[0m. Maneuver added.',
           False):
    pass

  elif catch(self, r_a >= body.SOI,
           'Failure',
           source,
           f'{param} not less than {body.name}\'s sphere of influence. Mission construction aborted!',
           True):
    return False

  elif catch(self, p_alt > a_alt,
             'Failure',
             source,
             'Given periapsis is greater than apoapsis. Mission construction aborted!',
             True):
    return False

  elif catch(self, not (0 <= inc < 360),
               'Failure',
               source,
               'Given inclination invalid. Choose between 0 and 360. Mission construction aborted!',
               True):
    return False

  elif catch(self, defaults == [p_alt, a_alt, inc],
           'Error',
           source,
           'Requested orbit is identical to current orbit. No changes applied.'):
    return False


  for moon in body.children:
    moon = moon()
    inner_SOI = moon.r_p - moon.SOI
    outer_SOI = moon.r_a + moon.SOI
    logic = (inner_SOI <= r_p <= outer_SOI) or (inner_SOI <= r_a <= outer_SOI)
    catch(self, logic, 'Warning',
          source,
          f'{param} intersects {moon.name}\'s sphere of influence. Maneuver added.')

  return True