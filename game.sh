#!/bin/bash
# My first script
BASEDIR $(cd $(dirname $0); pwd)
# Shellscript for runnning the game for linux users
export PYTHONPATH=$PYTHONPATH:$BASEDIR 	
python gamelogic/main.py -m DisplayWallTest.json
