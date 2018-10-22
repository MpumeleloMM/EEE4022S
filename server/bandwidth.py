#!/usr/bin/python
# Mpumelelo Mthethwa
# 12 September 2018

from subprocess import check_output;
from time import sleep, time;

interval = 120; # Bandwidth change interval (2 min)

# Bandwidth Modulation Values
bands = [[9, 5], [3.6, 2], [7.2, 4], [1.8, 1], [5.4, 3]];	# Formar -> [Cellular, Wi-Fi]

if (__name__ is not "__main__"):
	for band in bands:
		check_output(["./change.sh", "{:f}".format(band[0]), "{:f}".format(band[1])]);
		print (check_output(["tc", "qdisc", "show"]));
		sleep (interval);

