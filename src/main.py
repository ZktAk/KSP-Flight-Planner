from  Missions import * 
from Bodies import *
from Antennas import *
from CommNet import *


if __name__ == "__main__":
  mission = Munar_orbitor(50_000, 50_000, 0)
  mission.print_maneuver_bill(10)
  mission.print_power_bill(10)

  commNet = CommNet(tier=1)
  orbit = mission.complete()
  commNet.add_satellite(orbit, 14_000)
  commNet.satellite.add_antenna(Communotron_16)
  commNet.satellite.add_antenna(Communotron_16)

  
  max, min = commNet.satellite.direct_strength()
  print(f'\nMax %: {round(max*100)}%\nMin %: {round(min*100)}%')