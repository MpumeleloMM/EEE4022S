"""
	EEE4022S - Final Year Project: DASH Client/Server Implementation for MPTCP-aware SDN Datacentre Networks
	Mpumelelo Mthethwa (MTHMPU003)
	27 September 2018
"""

from pox.core import core;
from pox.lib.addresses import EthAddr, IPAddr;
from pox.lib.util import dpid_to_str, str_to_bool, str_to_dpid;
import pox.openflow.libopenflow_01 as of;
import pox.lib.packet as pkt;
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
		self.macToPort = {};
		self.macToIP = {};
		self.addr = 2;
		
		connection.addListeners(self);
		self.hold_down_expired = _flood_delay == 0;
	
	def _handle_PacketIn (self, event):
		
		packet = event.parsed;
	
		def drop (duration=None):
			
			if duration is not None:
				if not isinstance(duration, tuple):
					duration = (duration,duration);
				msg = of.ofp_flow_mod();
				msg.match = of.ofp_match.from_packet(packet);
				msg.idle_timeout = duration[0];
				msg.hard_timeout = duration[1];
				msg.buffer_id = event.ofp.buffer_id;
				self.connection.send(msg);
			elif event.ofp.buffer_id is not None:
				msg = of.ofp_packet_out();
				msg.buffer_id = event.ofp.buffer_id;
				msg.in_port = event.port;
				self.connection.send(msg);
				
		def flood (message = None):
			
			msg = of.ofp_packet_out();
			if time.time() - self.connection.connect_time >= _flood_delay:
				if self.hold_down_expired is False:
					self.hold_down_expired = True;
					log.info("%s: Flood hold-down expired -- flooding", dpid_to_str(event.dpid));
				if message is not None: log.debug(message);
				msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD));
			else:
				pass;
			msg.data = event.ofp;
			msg.in_port = event.port;
			self.connection.send(msg);
				
		"""Add MAC & IP to Tables"""
		self.macToPort[packet.src] = event.port;
		if (self.macToIP.get(packet.src, None)) is None:
			self.macToIP[packet.src] = "10.10.{:d}.{:d}".format((6-event.dpid%2), self.addr);
			self.addr += 1;
		
		if not self.transparent:
			if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
				drop();
				return;
				
		if packet.dst.is_multicast:
			flood();
		else:
			if packet.dst not in self.macToPort:
				flood("Port for %s unknown -- flooding" % (packet.dst,))
			else:
				port = self.macToPort[packet.dst];
				if port == event.port:
					log.warning("Same port for packet from %s -> %s on %s.%s.  Drop." % (packet.src, packet.dst, dpid_to_str(event.dpid), port));
					drop(10);
					return;
				log.debug("installing flow for %s.%i -> %s.%i" % (packet.src, event.port, packet.dst, port));
				msg = of.ofp_flow_mod();
				msg.match = of.ofp_match.from_packet(packet, event.port);
				msg.idle_timeout = 10;
				msg.hard_timeout = 30;
				msg.actions.append(of.ofp_action_output(port = port));
				msg.data = event.ofp;
				self.connection.send(msg);
		
		"""Catch and Process IPv4 Packets"""
		ip = packet.find("ipv4");
		
		if ip is not None:
			ip.ttl -= 1;
			"""Handle ICMP Time Exceeded Event"""
			if (ip.ttl == 0):
				log.debug ("TTL expired!!!");
		
				"""Create ICMP Time Exceeded Message"""
				icmp = pkt.icmp();
				icmp.type = pkt.TYPE_TIME_EXCEED;
				log.debug ("This is the ICMP error message {:s}".format(icmp.payload));

				"""Create IP Payload"""
				ipp = pkt.ipv4();
				ipp.protocol = ipp.ICMP_PROTOCOL;
				ipp.srcip = IPAddr(self.macToIP[packet.src]);
				ipp.dstip = packet.next.srcip;
				ipp.payload = icmp;
				log.debug ("This is the IP payload {:s}".format(ipp.payload));

				"""Create Ethernet Payload"""
				e = pkt.ethernet();
				e.src = packet.dst;
				e.dst = packet.src;
				e.type = e.IP_TYPE;
				e.payload = ipp;
				log.debug ("This is the Ethernet payload {:s}".format(e.payload));

				"""Send Packet the Original Source"""
				msg = of.ofp_packet_out();
				msg.actions.append(of.ofp_action_output(port=self.macToPort[packet.src]));
				msg.date = e.pack();
				msg.in_port = of.OFPP_NONE;
				event.connection.send(msg);


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
