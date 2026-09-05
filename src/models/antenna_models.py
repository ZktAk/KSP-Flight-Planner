class Communotron_16:
	cost = 300                  # Kerbucks
	mass = 0.005                # tons
	electricity = 6             # charge/Mit
	power = 500 * pow(10,3)     # m
	packet_size = 2             # Mits
	speed = 10/3                # Mits/s
	is_relay = False
	compatibility = 1

class Communotron_16_S:
	cost = 300                  # Kerbucks
	mass = 0.015                # tons
	electricity = 6             # charge/Mit
	power = 500 * pow(10,3)     # m
	packet_size = 2             # Mits
	speed = 10 / 3              # Mits/s
	is_relay = False
	compatibility = 0

class Communotron_DTS_M1:
	cost = 900                  # Kerbucks
	mass = 0.05                 # tons
	electricity = 6             # charge/Mit
	power = 2 * pow(10,9)       # m
	packet_size = 2             # Mits
	speed = 5.7142857142857     # Mits/s
	is_relay = False
	compatibility = 0.75

class Communotron_HG_55:
	cost = 1200                 # Kerbucks
	mass = 0.075                # tons
	electricity = 20/3          # charge/Mit
	power = 15 * pow(10,9)      # m
	packet_size = 3             # Mits
	speed = 20                  # Mits/s
	is_relay = False
	compatibility = 0.75

class Communotron_88_88:
	cost = 1500                 # Kerbucks
	mass = 0.1                  # tons
	electricity = 10            # charge/Mit
	power = 100 * pow(10,9)     # m
	packet_size = 2             # Mits
	speed = 20                  # Mits/s
	is_relay = False
	compatibility = 0.75

class HG_5_High_Gain_Antenna:
	cost = 600                  # Kerbucks
	mass = 0.07                 # tons
	electricity = 9             # charge/Mit
	power = 5 * pow(10,6)       # m
	packet_size = 2             # Mits
	speed = 5.7142857142857     # Mits/s
	is_relay = True
	compatibility = 0.75

class RA_2_relay_Antenna:
	cost = 1800                 # Kerbucks
	mass = 0.15                 # tons
	electricity = 24            # charge/Mit
	power = 2 * pow(10,9)       # m
	packet_size = 1             # Mits
	speed = 2.8571428571429     # Mits/s
	is_relay = True
	compatibility = 0.75

class RA_15_relay_Antenna:
	cost = 2400                 # Kerbucks
	mass = 0.3                  # tons
	electricity = 12            # charge/Mit
	power = 15 * pow(10,9)      # m
	packet_size = 2             # Mits
	speed = 5.7142857142857     # Mits/s
	is_relay = True
	compatibility = 0.75

class RA_100_relay_Antenna:
	cost = 3000                 # Kerbucks
	mass = 0.65                 # tons
	electricity = 6             # charge/Mit
	power = 100 * pow(10,9)     # m
	packet_size = 4             # Mits
	speed = 11.428571428571     # Mits/s
	is_relay = True
	compatibility = 0.75


class Multi:
	def __init__(self):
		self.antennas = []

	def add(self, antenna):
		self.antennas.append(antenna)

	def combined_power(self):

		c_numerator = sum(antenna.power * antenna.compatibility for antenna in self.antennas)
		sum_power = sum(antenna.power for antenna in self.antennas)
		max_power = max(antenna.power for antenna in self.antennas)

		c = c_numerator / sum_power
		total_power = max_power * pow(sum_power/max_power, c)

		return total_power


# Example usage
def Test_ants():
	test = Multi()
	test.add(Communotron_16)
	test.add(Communotron_16)
	power = test.combined_power()
	print(f'{round(power/1000):,} km')