#!/bin/bash
# Mpumelelo Mthethwa
# 24 September 2018

clear;

curl http://127.0.0.1:8080/wm/staticentrypusher/clear/all/json;

./staticflowpusher.py

for idx in 1 2 3 4 5 6 7 8; do
	ovs-ofctl dump-flows s$idx
done;
