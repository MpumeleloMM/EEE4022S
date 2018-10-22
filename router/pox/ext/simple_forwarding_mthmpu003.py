"""
	EEE4022S - Final Year Project: DASH Client/Server Implementation for MPTCP-aware SDN Datacentre Networks
	Mpumelelo Mthethwa (MTHMPU003)
	27 September 2018
"""

from pox.core import core;
from pox.lib.addresses import EthAddr, IPAddr;
from pox.lib.util import dpid_to_str, str_to_bool, str_to_dpid;
from subprocess import check_output;
import pox.openflow.libopenflow_01 as of;
import pox.lib.packet as pkt;
import re;
import time;

log = core.getLogger();

# We don't want to flood immediately when a switch connects.
# Can be overriden on commandline.
_flood_delay = 0;

""" Simple Bi-Directional Forwarding Application with ICMP Responses"""
class SimpleSwitch (object):
	
	def __init__ (self, connection, transparent):
		self.connection = connection;
		self.transparent = transparent;
		
		"""DP Flow Table Register"""
		self.flowTabReg = [];
		
		"""MAC & IP Address Tables"""
		self.arp_table = {};
		self.mac_to_port = {};
		self.mac_to_ip = {};
		self.addr = 2;
		
		ips = check_output(["hostname", "-I"]).split();
		macs = re.findall(r"[\w\W\d]{2}:[\w\W\d]{2}:[\w\W\d]{2}:[\w\W\d]{2}:[\w\W\d]{2}:[\w\W\d]{2}", check_output(["ifconfig"]));
		
		for i in range(len(ips)):
			self.arp_table[IPAddr(ips[i])] = EthAddr(macs[i]);
		
		connection.addListeners(self);
		self.hold_down_expired = _flood_delay == 0;
	
	def _handle_PacketIn (self, event):
		
		if event.dpid not in [1, 2, 7, 8]:
			return;
		
		packet = event.parsed;
				
		"""Add MAC & IP to Tables"""
		self.mac_to_port[packet.src] = event.port;
		if (self.mac_to_ip.get(packet.src, None)) is None:
			self.mac_to_ip[packet.src] = "10.10.{:d}.{:d}".format((6-event.dpid%2), self.addr);
			self.addr += 1;
		
		"""Catch and Process ARP Packets"""
		if isinstance(packet.next, pkt.arp):
			if event.dpid not in [1, 2, 7, 8]:
				return;
			elif packet.next.opcode == pkt.arp.REQUEST:
				#print (packet.next.hwtype, packet.next.prototype, str(packet.next.hwsrc), str(packet.next.hwdst), str(packet.next.hwlen), packet.next.opcode, packet.next.protolen, str(packet.next.protosrc), str(packet.next.protodst));
				r = pkt.arp();
				r.hwtype = packet.next.hwtype;
				r.prototype = packet.next.prototype;
				r.hwlen = packet.next.hwlen;
				r.protolen = packet.next.protolen;
				r.opcode = pkt.arp.REPLY;
				r.hwdst = packet.next.hwsrc;
				mac = self.arp_table.get(packet.next.protodst, None);
				if mac is not None:
					r.hwsrc = mac;
					r.protodst = packet.next.protosrc;
					r.protosrc = packet.next.protodst;
					e = pkt.ethernet(type=packet.type, src=r.hwsrc, dst=r.hwdst);
					e.payload = r;
					log.info ("{:s} answering ARP for {:s}".format(dpid_to_str(event.dpid), str(r.protosrc)));
					msg = of.ofp_packet_out(data=e.pack(), in_port=event.port, actions=of.ofp_action_output(port = of.OFPP_LOCAL));
					self.connection.send(msg);
		
		"""Catch and Process IPv4 Packets"""
		if isinstance(packet.next, pkt.ipv4):
			#packet.next.ttl -= 1;
			log.debug ("({:d}.{:d}): {:s} -> {:s}".format(event.dpid, event.port, packet.next.srcip, packet.next.dstip));
			return;

class simple_forwarding (object):
	
	def __init__ (self, transparent, ignore=None):
		core.openflow.addListeners(self);
		self.transparent = transparent;
		self.ignore = set(ignore) if ignore else ();
	
	def _handle_ConnectionUp (self, event):
		if event.dpid in self.ignore:
			log.debug ("Ignoring connection {:s}".format(event.connection,));
			return;
		
		log.debug ("Connection {:s}".format(event.connection,));
		SimpleSwitch (event.connection, self.transparent);

def launch (transparent=False, hold_down=_flood_delay, ignore=None):
	
	try:
		global _flood_delay;
		_flood_delay = int(str(hold_down), 10);
		assert _flood_delay >= 0;
	except:
		raise RuntimeError("Expected hold-down to be a number");
	
	if ignore:
		ignore = ignore.replace(',', ' ').split();
		ignore = set(str_to_dpid(dpid) for dpid in ignore);
	
	core.registerNew(simple_forwarding, str_to_bool(transparent), ignore);
