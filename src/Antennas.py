
class Communotron_16:
	cost = 300                  # Kerbucks
	mass = 0.005                # tons
	electricity = 6             # charge/Mit
	power = 500 * pow(10,3)     # m
	packet_size = 2             # Mits
	speed = 10/3                # Mits/s
	relay = False
	compatibility = 1

class Communotron_16_S:
	cost = 300                  # Kerbucks
	mass = 0.015                # tons
	electricity = 6             # charge/Mit
	power = 500 * pow(10,3)     # m
	packet_size = 2             # Mits
	speed = 10 / 3              # Mits/s
	relay = False
	compatibility = 0

class Communotron_DTS_M1:
	cost = 900                  # Kerbucks
	mass = 0.05                 # tons
	electricity = 6             # charge/Mit
	power = 2 * pow(10,9)       # m
	packet_size = 2             # Mits
	speed = 5.7142857142857     # Mits/s
	relay = False
	compatibility = 0.75

class Communotron_HG_55:
	cost = 1200                 # Kerbucks
	mass = 0.075                # tons
	electricity = 20/3          # charge/Mit
	power = 15 * pow(10,9)      # m
	packet_size = 3             # Mits
	speed = 20                  # Mits/s
	relay = False
	compatibility = 0.75

class Communotron_88_88:
	cost = 1500                 # Kerbucks
	mass = 0.1                  # tons
	electricity = 10            # charge/Mit
	power = 100 * pow(10,9)     # m
	packet_size = 2             # Mits
	speed = 20                  # Mits/s
	relay = False
	compatibility = 0.75

class HG_5_High_Gain_Antenna:
	cost = 600                  # Kerbucks
	mass = 0.07                 # tons
	electricity = 9             # charge/Mit
	power = 5 * pow(10,6)       # m
	packet_size = 2             # Mits
	speed = 5.7142857142857     # Mits/s
	relay = True
	compatibility = 0.75

class RA_2_Relay_Antenna:
	cost = 1800                 # Kerbucks
	mass = 0.15                 # tons
	electricity = 24            # charge/Mit
	power = 2 * pow(10,9)       # m
	packet_size = 1             # Mits
	speed = 2.8571428571429     # Mits/s
	relay = True
	compatibility = 0.75

class RA_15_Relay_Antenna:
	cost = 2400                 # Kerbucks
	mass = 0.3                  # tons
	electricity = 12            # charge/Mit
	power = 15 * pow(10,9)      # m
	packet_size = 2             # Mits
	speed = 5.7142857142857     # Mits/s
	relay = True
	compatibility = 0.75

class RA_100_Relay_Antenna:
	cost = 3000                 # Kerbucks
	mass = 0.65                 # tons
	electricity = 6             # charge/Mit
	power = 100 * pow(10,9)     # m
	packet_size = 4             # Mits
	speed = 11.428571428571     # Mits/s
	relay = True
	compatibility = 0.75


class Multi:
	def __init__(self):
		self.antennas = []

	def add(self, antenna):
		self.antennas.append(antenna)

	def combined_power(self):
		c_numerator = 0
		sum_power = 0

		for antenna in self.antennas:
			c_numerator += antenna.power * antenna.compatibility
			sum_power += antenna.power

		c = c_numerator / sum_power
		max_power = max(antenna.power for antenna in self.antennas)
		total_power = max_power * pow(sum_power/max_power, c)
		return total_power


# Example usage
if __name__ == "__main__":
	test = Multi()
	test.add(Communotron_16)
	test.add(Communotron_16)
	power = test.combined_power()
	print(f'{round(power/1000):,} km')