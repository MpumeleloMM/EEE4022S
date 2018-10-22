#!/bin/bash
# EEE4022S - Final Year Project: DASH Client/Server Implementation for MPTCP-Aware SDN Datacentre Networks
# Connect mininet to host interfaces (Add Ports)
# Mpumelelo Mthethwa (MTHMPU003)
# 21 Septemeber 2018

clear

declare -a dev=("enp0s8" "enp0s9" "enp0s10" "enp0s16");
declare -a sw=("$@");

for i in 1 2 3 4; do
	ip a flush dev ${dev[$i-1]}
	ip a add 10.10.$i.2/24 dev ${sw[$i-1]}
	ovs-vsctl add-port ${sw[$i-1]} ${dev[$i-1]}
	ip link set ${sw[$i-1]} up
done;
