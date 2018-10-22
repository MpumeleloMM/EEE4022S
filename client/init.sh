#!/bin/bash
# Commands to run at boot
# Mpumelelo Mthethwa
# 12 September 2018

clear

tc qdisc add dev enp0s8 root netem rate 9Mbit delay 18ms
tc qdisc add dev enp0s9 root netem rate 5Mbit delay 2.5ms

# Set Forwarding Rules
ip r add 10.10.3.0/24 via 10.10.1.2 dev enp0s8
ip r add 10.10.4.0/24 via 10.10.2.2 dev enp0s9
#ip r add default via 10.10.1.3 dev enp0s8

route -n
