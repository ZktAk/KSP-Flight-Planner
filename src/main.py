from  Missions import * 
from Bodies import *
from Antennas import *
from CommNet import *


if __name__ == "__main__":

  
  mission = Duna_launch()
  orbit = mission.complete()

  commNet = CommNet(tier=3)
  relay = Satellite(orbit, 0, commNet.DSN, comm_type='Relay')
  relay.add_antenna(RA_15_relay_Antenna)
  relay.add_antenna(RA_100_relay_Antenna)
  commNet.add_satellite(relay)  

  relay2 = Satellite(orbit, 0, commNet.DSN, comm_type='Relay')
  relay2.add_antenna(RA_15_relay_Antenna)
  relay2.add_antenna(RA_15_relay_Antenna)
  commNet.add_satellite(relay2)

  mission2 = Duna_launch(100_000)
  mission2.print_maneuver_bill(10)
  mission2.print_power_bill(10)
  orbit2 = mission2.complete()
  test_sat = Satellite(orbit2, 14_000, commNet.DSN, comm_type='Direct')
  test_sat.add_antenna(Communotron_16)
  commNet.add_satellite(test_sat)
  
  commNet.query_signal_strength(test_sat)
