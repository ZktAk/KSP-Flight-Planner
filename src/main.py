from  Missions import * 
from Bodies import *
from Antennas import *
from CommNet import *


if __name__ == "__main__":
  mission = Munar_orbitor(50_000, 50_000, 0)
  mission.print_maneuver_bill(10)
  capacit = mission.print_power_bill(10)
  orbit = mission.complete()

  commNet = CommNet(tier=1)
  satellite = Satellite(orbit, capacit, commNet.DSN)
  satellite.add_antenna(Communotron_16)
  satellite.add_antenna(Communotron_16)
  
  commNet.add_satellite(satellite)
  commNet.has_path(satellite)
  
  max, min = satellite.direct_strength()
  print(f'\nMax %: {round(max*100)}%\nMin %: {round(min*100)}%')