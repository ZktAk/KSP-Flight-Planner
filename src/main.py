from  Missions import * 
from Bodies import *
from Antennas import *
from CommNet import *


if __name__ == "__main__":

  # Duna_test = Mission(origin=Duna)
  # Duna_test.Launch()
  # Duna_test.print_maneuver_bill(10)
  mission = Duna_orbitor()
  # mission.print_maneuver_bill(10)
  # capacit = mission.print_power_bill(10)
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

  max, min = relay._strength()
  print(f'\nRelay1 Max signal strength %: {round(max*100)}%\nRelay1 Min signal strength %: {round(min*100)}%')

  max, min = relay2._strength()
  print(f'\nRelay2 Max signal strength %: {round(max*100)}%\nRelay2 Min signal strength %: {round(min*100)}%')

  mission2 = Duna_orbitor(100_000)  
  orbit2 = mission2.complete()
  test_sat = Satellite(orbit2, 14_000, commNet.DSN, comm_type='Direct')
  test_sat.add_antenna(Communotron_16)
  commNet.add_satellite(test_sat)

  target_strength = 0.7
  
  commNet.test_signal_strength(test_sat, target_strength)
