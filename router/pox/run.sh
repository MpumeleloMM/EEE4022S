#!/bin/bash

clear

if [ $# = 0 ]; then
	./pox.py log.level --DEBUG openflow.of_01
else
	./pox.py log.level --DEBUG openflow.of_01 $1
fi
