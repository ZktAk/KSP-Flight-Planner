import math
class Orbit:
  def __init__(self, body, p_alt, a_alt, inc):
    self.parent = body
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