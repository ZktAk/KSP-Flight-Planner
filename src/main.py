from  Missions import Mission 
from Bodies import *
from Antennas import *
import CommNet


if __name__ == "__main__":
  print('hello')
  mission = Munar_orbitor(50_000, 50_000, 0)
  mission.print_maneuver_bill(10)
  mission.print_power_bill(10)

  orbit = mission.final_orbit()
  satellite = CommNet.Satellite(orbit, 14_000, CommNet.DSN_tiers[1])
  satellite.add_antenna(Communotron_16)
  satellite.add_antenna(Communotron_16)
  max, min = satellite.direct_strength()
  print(f'\nMax %: {round(max*100)}%\nMin %: {round(min*100)}% fag')