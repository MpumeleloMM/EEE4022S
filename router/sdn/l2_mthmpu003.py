#!/usr/bin/python
# Mpumelelo Mthethwa
# 19 August 2018

"""
An OpenFlow 1.0 L2 learning switch implementation.
"""

from ryu.base import app_manager;
from ryu.controller import ofp_event;
from ryu.controller.handler import MAIN_DISPATCHER;
from ryu.controller.handler import set_ev_cls;
from ryu.ofproto import ofproto_v1_2;
from ryu.lib.mac import haddr_to_bin;
from ryu.lib.packet import packet;
from ryu.lib.packet import ethernet;
from ryu.lib.packet import ether_types;

class SimpleSwitch (app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_2.OFP_VERSION];
	
	def __init__(self, *args, **kwargs):
		super (SimpleSwitch, self).__init__(*args, **kwargs);
		self.mac_to_port = {};
		
	def add_flow(self, datapath, in_port, dst, actions):
		ofproto = datapath.ofproto;
		match = datapath.ofproto_parser.OFPMatch (in_port=in_port, dl_dst=haddr_to_bin(dst));
		mod = datapath.ofproto_parser.OFPFlowMod (datapath=datapath, match=match, cookie=0, command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0, priority=ofproto.OFP_DEFAULT_PRIORITY, flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions);
		datapath.send_msg (mod);
		
	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def _packet_in_handler(self, ev):
		msg = ev.msg;
		self.logger.info (str(type(msg.match)));
		datapath = msg.datapath;
		ofproto = datapath.ofproto;
		
		pkt = packet.Packet (msg.data);
		eth = pkt.get_protocol (ethernet.ethernet);
		
		if eth.ethertype == ether_types.ETH_TYPE_LLDP:
			# ignore lldp packet
			return;
			
		dst = eth.dst;
		src = eth.src;
		
		dpid = datapath.id;
		self.mac_to_port.setdefault(dpid, {});
		
		#self.logger.info("packet in %s %s %s %s", dpid, src, dst, ofproto_v1_2.OFPP_IN_PORT);
		self.logger.info("packet in %s %s %s %s", dpid, src, dst, ofproto_v1_2.OFPP_IN_PORT);
		
		# learn a mac address to avoid FLOOD next time.
		self.mac_to_port[dpid][src] = ofproto_v1_2.OFPP_IN_PORT;
		
		if dst in self.mac_to_port[dpid]:
			out_port = self.mac_to_port[dpid][dst];
		else:
			out_port = ofproto.OFPP_FLOOD;
			
		actions = [datapath.ofproto_parser.OFPActionOutput(out_port)];
		
		# install a flow to avoid packet_in next time
		if out_port != ofproto.OFPP_FLOOD:
			self.add_flow(datapath, ofproto_v1_2.OFPP_IN_PORT, dst, actions);
			
		data = None;
		if msg.buffer_id == ofproto.OFP_NO_BUFFER:
			data = msg.data;
			
		out = datapath.ofproto_parser.OFPPacketOut (datapath=datapath, buffer_id=msg.buffer_id, in_port=ofproto_v1_2.OFPP_IN_PORT, actions=actions, data=data);
		datapath.send_msg (out);
	
	@set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
	def _port_status_handler(self, ev):
		msg = ev.msg;
		reason = msg.reason;
		port_no = msg.desc.port_no;
		
		ofproto = msg.datapath.ofproto;
		if reason == ofproto.OFPPR_ADD:
			self.logger.info("port added %s", port_no);
		elif reason == ofproto.OFPPR_DELETE:
			self.logger.info("port deleted %s", port_no);
		elif reason == ofproto.OFPPR_MODIFY:
			self.logger.info("port modified %s", port_no);
		else:
			self.logger.info("Illeagal port state %s %s", port_no, reason);
