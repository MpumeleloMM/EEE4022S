#!/usr/bin/python
# Mpumelelo Mthethwa (MTHMPU003)
# EEE4087F-B: Lab 1 (Part 2)
# SDN
# Implementing a Layer-2 Firewall using POX and Mininet

from mininet.net import Mininet;
from mininet.node import RemoteController;
from mininet.cli import CLI;
from mininet.log import setLogLevel, info;
from mininet.util import dumpNodeConnections

def treeTopo():
    net = Mininet (controller=RemoteController);

    # Add controller
    net.addController ("c0");

    # Add hosts
    h = [
            net.addHost ("h1", mac="00:00:00:00:00:01"),
            net.addHost ("h2", mac="00:00:00:00:00:02"),
            net.addHost ("h3", mac="00:00:00:00:00:03"),
            net.addHost ("h4", mac="00:00:00:00:00:04"),
            net.addHost ("h5", mac="00:00:00:00:00:05"),
            net.addHost ("h6", mac="00:00:00:00:00:06"),
            net.addHost ("h7", mac="00:00:00:00:00:07"),
            net.addHost ("h8", mac="00:00:00:00:00:08")
        ];

    # Add switches
    s = [
            net.addSwitch ("s1"),
            net.addSwitch ("s2"),
            net.addSwitch ("s3"),
            net.addSwitch ("s4"),
            net.addSwitch ("s5"),
            net.addSwitch ("s6"),
            net.addSwitch ("s7"),
        ];

    level = [s[0], [s[1], s[4]], [s[2], s[3], s[5], s[6]]];

    # Create links
    for i in range(len(level[2])):
		for j in range (2):
			net.addLink (h[2*i + j], level[2][i]);

    for i, l in enumerate (level[1]):
        net.addLink (level[0], l);
        net.addLink (l, level[2][2*i]);
        net.addLink (l, level[2][2*i + 1]);

    # Start network
    net.start();
    dumpNodeConnections(net.hosts);
    dumpNodeConnections(net.switches);

    # Run CLI
    CLI (net);
    #net.pingAll();

    # Stop network
    net.stop();

if (__name__ == "__main__"):
    setLogLevel("info");
    treeTopo();
