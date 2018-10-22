#!/bin/bash
# Commands to run at boot
# Mpumelelo Mthethwa
# 12 September 2018

clear

if [ $# = 2 ]; then
	tc qdisc change dev enp0s8 root netem rate $1Mbit delay 18ms
	tc qdisc change dev enp0s9 root netem rate $2Mbit delay 2.5ms
fi;
