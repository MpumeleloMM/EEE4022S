#!/usr/bin/python
# Mpumelelo Mthethwa
# 20 September 2018

import httplib;
import json;

from sys import argv;

class StaticFlowPusher (object):
	def __init__ (self, server):
		self.server = server;
	
	def get (self, data):
		ret = self.rest_call({},"GET");
		return json.loads(ret[2]);
		
	def set(self, data):
		ret = self.rest_call(data, 'POST');
		return ret[0] == 200;
		
	def remove(self, objtype, data):
		ret = self.rest_call(data, 'DELETE');
		return ret[0] == 200;
		
	def rest_call(self, data, action):
		path = '/wm/staticflowpusher/json';
		headers = {'Content-type': 'application/json', 'Accept': 'application/json'};
		body = json.dumps(data);
		conn = httplib.HTTPConnection(self.server, 8080);
		conn.request(action, path, body, headers);
		response = conn.getresponse();
		ret = (response.status, response.reason, response.read());
		print (ret);
		conn.close();
		return ret;

if (__name__=="__main__"):
	pusher = StaticFlowPusher("127.0.0.1" if len(argv)!=2 else argv[1]);
	
	for idx in range(1,9):
		pusher.set({"switch":"00:00:00:00:00:00:00:{:02d}".format(idx),"name":"flow_mod_{:d}".format(idx*2 - 1),"cookie":"0","priority":"32768","in_port":"1","active":"true","actions":"output=2"});
		pusher.set({"switch":"00:00:00:00:00:00:00:{:02d}".format(idx),"name":"flow_mod_{:d}".format(idx*2),"cookie":"0","priority":"32768","in_port":"2","active":"true","actions":"output=1"});
		
	"""flow = [{"switch":"00:00:00:00:00:00:00:01","name":"flow_mod_01","cookie":"0","priority":"32768","in_port":"1","active":"true","actions":"output=2"},
			{"switch":"00:00:00:00:00:00:00:01","name":"flow_mod_02","cookie":"0","priority":"32768","in_port":"2","active":"true","actions":"output=1"},
			{"switch":"00:00:00:00:00:00:00:02","name":"flow_mod_03","cookie":"0","priority":"32768","in_port":"1","active":"true","actions":"output=2"},
			{"switch":"00:00:00:00:00:00:00:02","name":"flow_mod_04","cookie":"0","priority":"32768","in_port":"2","active":"true","actions":"output=1"},
			{"switch":"00:00:00:00:00:00:00:03","name":"flow_mod_05","cookie":"0","priority":"32768","in_port":"1","active":"true","actions":"output=2"},
			{"switch":"00:00:00:00:00:00:00:03","name":"flow_mod_06","cookie":"0","priority":"32768","in_port":"2","active":"true","actions":"output=1"},
			{"switch":"00:00:00:00:00:00:00:04","name":"flow_mod_07","cookie":"0","priority":"32768","in_port":"1","active":"true","actions":"output=2"},
			{"switch":"00:00:00:00:00:00:00:04","name":"flow_mod_08","cookie":"0","priority":"32768","in_port":"2","active":"true","actions":"output=1"},
			{"switch":"00:00:00:00:00:00:00:05","name":"flow_mod_09","cookie":"0","priority":"32768","in_port":"1","active":"true","actions":"output=2"},
			{"switch":"00:00:00:00:00:00:00:05","name":"flow_mod_10","cookie":"0","priority":"32768","in_port":"2","active":"true","actions":"output=1"},
			{"switch":"00:00:00:00:00:00:00:06","name":"flow_mod_11","cookie":"0","priority":"32768","in_port":"1","active":"true","actions":"output=2"},
			{"switch":"00:00:00:00:00:00:00:06","name":"flow_mod_12","cookie":"0","priority":"32768","in_port":"2","active":"true","actions":"output=1"},
			{"switch":"00:00:00:00:00:00:00:07","name":"flow_mod_13","cookie":"0","priority":"32768","in_port":"1","active":"true","actions":"output=2"},
			{"switch":"00:00:00:00:00:00:00:07","name":"flow_mod_14","cookie":"0","priority":"32768","in_port":"2","active":"true","actions":"output=1"},
			{"switch":"00:00:00:00:00:00:00:08","name":"flow_mod_15","cookie":"0","priority":"32768","in_port":"1","active":"true","actions":"output=2"},
			{"switch":"00:00:00:00:00:00:00:08","name":"flow_mod_16","cookie":"0","priority":"32768","in_port":"2","active":"true","actions":"output=1"}]
	for idx in range(len(flow)):
		pusher.set(flow[idx]);"""
