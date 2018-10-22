#!/bin/bash
# Commands to run at boot
# Mpumelelo Mthethwa
# 12 September 2018

clear

tc qdisc add dev enp0s8 root netem rate 9Mbit delay 18ms
tc qdisc add dev enp0s9 root netem rate 5Mbit delay 2.5ms

ips=(`hostname -I`)
dev=("enp0s3" "enp0s8" "enp0s9")
sub=(2 3 4)

# Create two different the routing tables, that we use based on the source address
#ip rule add from 10.10.3.3 table 1
#ip rule add from 10.10.4.3 table 2
for i in 1 2; do
	ip rule add from ${ips[$i]} table $i
done;

# Configure the two different routing tables
#ip route add 10.10.3.0/24 dev enp0s8 scope link table 1
#ip route add default via 10.10.3.2 dev enp0s8 table 1
#ip route add 10.10.4.0/24 dev enp0s9 scope link table 2
#ip route add default via 10.10.4.2 dev enp0s9 table 2
for i in 1 2; do
	ip route add 10.10.${sub[$i]}.0/24 dev ${dev[$i]} scope link table $i
	ip route add default via ${ips[$i]} dev ${dev[$i]} table $i
done;

# Default route for the selection process of normal internet traffic
ip route add default scope global nexthop via 10.0.2.2 dev enp0s3

#route -n
