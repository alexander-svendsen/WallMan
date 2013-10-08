#!/bin/bash
# My first script
BASEDIR $(cd $(dirname $0); pwd)
export PYTHONPATH=$PYTHONPATH:$BASEDIR 	
python gamelogic/main.py -m DisplayWallTest.json
