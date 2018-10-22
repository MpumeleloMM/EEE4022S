#!/bin/bash

clear

if [ $# = 0 ]; then
	ryu-manager simple_forward_mthmpu003
else
	ryu-manager $1
fi
