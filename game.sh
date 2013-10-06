#!/bin/bash
# Shellscript for runnning the game for linux users

BASEDIR=..
export PYTHONPATH=$PYTHONPATH:$BASEDIR 	
python gamelogic/main.py -m DisplayWallTest.json
