#!/usr/bin/python
# EEE4022S - Final Year Project: DASH Client/Server Implementation for MPTCP-Aware SDN Datacentre Networks
# Mpumelelo Mthethwa (MTHMPU003)
# 19 August 2018

import mininet.node;
import mininet.link;

from mininet.cli import CLI;
from mininet.link import Intf, OVSIntf, TCIntf, TCLink;
from mininet.log import setLogLevel, info;
from mininet.net import Mininet;
from mininet.node import OVSSwitch, RemoteController;
from mininet.util import dumpNodeConnections;


from argparse import ArgumentParser;
from numpy import mean, std;
from subprocess import check_output;
import math;
import os;
import re;

parser = ArgumentParser (description="Mininet MPCTP test framework");
parser.add_argument ("--cellular", "-C", type=int, help="Set number of hops in the cellular network", default=20);
parser.add_argument ("--distance", "-D", type=float, help="Set user's distance (radius) from the Base Transceiver Station", default=1);
parser.add_argument ("--ex-hosts", "-E", help="Use external hosts, i.e. not spawed by Mininet", action="store_true");
parser.add_argument ("--loss-cellular", "-Lc", type=float, help="Percentage of packet loss on the celluar interface", default=1);
parser.add_argument ("--loss-wifi", "-Lw", type=float, help="Percentage of packet loss Wi-Fi interface", default=1);
parser.add_argument ("--remote-address", "-R", type=str, help="Set remote controller listening address", default="127.0.0.1");
parser.add_argument ("--remote-port", "-P", type=int, help="Set remote controller listening port", default=6653);
parser.add_argument ("--share-wifi", "-S", type=int, help="Set number of devices sharing the Wi-Fi connection", default=1);
parser.add_argument ("--wifi", "-W", type=int, help="Set number of hops in the Wi-Fi network", default=17);

args = parser.parse_args();

linkParams =	[
					{"bw":9.0/args.distance, "delay":"36ms", "loss":args.loss_cellular, "max_queue_size":1000},				# Cellular Network Link Parameters
					{"bw":5.0/float(args.share_wifi), "delay":"5ms", "loss":args.loss_wifi, "max_queue_size":1000}			# Wi-Fi Link Parameters
				];

def mptcpTopo (cellular, wifi, externalHosts):
	net = Mininet (link=TCLink, switch=OVSSwitch, autoSetMacs=True);
	h = [];
	s = {};
	addr = 1;
		
	# Add Controller
	net.addController ("c0", controller=RemoteController, ip=args.remote_address, port=args.remote_port);
			
	# Add Switches
	for i in range(0, cellular*2, 2):
		s["{:d}".format(i)] = (net.addSwitch("s{:d}".format(i+1), protocols="OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13"));
	
	for i in range(1, wifi*2, 2):
		s["{:d}".format(i)] = (net.addSwitch("s{:d}".format(i+1), protocols="OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13"));
	
	# Create Links
	if not externalHosts:
		# Datacentre
		h.append(net.addHost("h1"));
		net.addLink(h[0], s["0"], **(linkParams[0]));
		net.addLink(h[0], s["1"], **(linkParams[1]));
		h[0].setIP(intf="h1-eth1", ip="10.0.0.3");
		
		# User Equipment
		h.append(net.addHost("h2"));
		net.addLink(h[1], s["{:d}".format(cellular*2 - 2)], **(linkParams[0]));
		net.addLink(h[1], s["{:d}".format(wifi*2 - 1)], **(linkParams[1]));
		h[1].setIP(intf="h2-eth1", ip="10.0.0.4");
	
		# Cellular (odd) / WiFi (even)
	for i in range (0, cellular*2, 2):
		if ((i+2) < cellular*2):
			net.addLink (s["{:d}".format(i)], s["{:d}".format(i+2)], **(linkParams[0]));
	for i in range (1, wifi*2, 2):
		if ((i+2) < wifi*2):
			net.addLink (s["{:d}".format(i)], s["{:d}".format(i+2)], **(linkParams[1]));
	
	# Start Network
	net.start();
	if not externalHosts:
		h[0].cmd("ip r add 10.0.0.2 via 10.0.0.1 dev h1-eth0");
		h[0].cmd("ip r add 10.0.0.4 via 10.0.0.3 dev h1-eth1");
		h[1].cmd("ip r add 10.0.0.1 via 10.0.0.2 dev h2-eth0");
		h[1].cmd("ip r add 10.0.0.3 via 10.0.0.4 dev h2-eth1");
	
	# Connect to External Hosts using Ports and External Interfaces
	if externalHosts:
		"""intfs = {"0":"enp0s8", "1":"enp0s9", "{:d}".format(cellular*2 - 2):"enp0s10", "{:d}".format(wifi*2 - 1):"enp0s16"};
		#intfs = {"0":"s1-eth2", "1":"s2-eth2", "{:d}".format(cellular*2 - 2):"s{:d}-eth2".format(cellular*2 - 1), "{:d}".format(wifi*2 - 1):"s{:d}-eth2".format(wifi*2)};
		for k in intfs.keys():
			check_output(["ovs-vsctl", "add-port", s[k].name, intfs[k]]);
			check_output(["ifconfig", intfs[k], "0"]);
			check_output(["dhclient", intfs[k]]);
			#_intf = TCIntf (node=s[k], name=intfs[k]);
			#print(_intf);
			#s[k].addIntf(intf=_intf);"""
		print (check_output(["./ports.sh", s["0"].name, s["1"].name, s["{:d}".format(cellular*2 - 2)].name, s["{:d}".format(wifi*2 - 1)].name]));
	
	# List All OVSSwtiches
	bridgeSet = set();
	for b in net.switches:
		bridgeSet.add(b.name);
	
	# Delete/Add Flows Manually
	#for b in bridgeSet:
	#	check_output(["ovs-ofctl", "del-flows", "{:s}".format(b)]);
	#	check_output(["ovs-ofctl", "add-flows", "{:s}".format(b), "flows.txt"]);
	
	# Run Command Line Interface
	CLI (net);
	
	# Stop Network
	net.stop();


if (__name__=="__main__"):
	setLogLevel("info");
	mptcpTopo(cellular=args.cellular, wifi=args.wifi, externalHosts=args.ex_hosts);
