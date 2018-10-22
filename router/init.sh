#!/bin/bash
# Commands to run at boot
# Mpumelelo Mthethwa
# 12 September 2018

clear;

if [ $# -ne 0 ]; then
	if [ $1 = "init" ]; then
		# Initial Stuff
		apt-get upgrade
		apt-get update
		apt-get install build-essential module-assistant dkms ant maven python-dev
		apt-get install geany* eclipse* gparted wireshark
		m-a prepare
	fi;
else
	# Enable IP Forwarding
	echo 1 > /proc/sys/net/ipv4/ip_forward
	

	# Configure IP Tables
		# Flush Tables
	#iptables -t filter -F
	#iptables -t mangle -F
	#iptables -t nat -F
	#iptables -t raw -F
	#iptables -t security -F
	#iptables -F
		# Delete Chains
	#iptables -X
		# Read Rules from File
	#iptables-restore /home/router/iptables.init
	#iptables -t nat -A OUTPUT -p udp --dport 53 -j DNAT --to 23.226.230.72:5353
	#iptables -t nat -A OUTPUT -p tcp --dport 53 -j DNAT --to 23.226.230.72:5353
	#iptables -t nat -A POSTROUTING -o enp0s3 -j MASQUERADE
	#for dev in "enp0s8" "enp0s9" "enp0s10" "enp0s16"; do
	#	iptables -A FORWARD -i $dev -j ACCEPT
	#done;
	
	iptables -t filter --list
	iptables -t nat --list
	# tcpdump -eni enp0s8
fi;
