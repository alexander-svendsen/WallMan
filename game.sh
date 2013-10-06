#!/bin/bash
# Shellscript for runnning the game for linux users

BASEDIR=$(dirname $BASH_SOURCE )
export PYTHONPATH=$PYTHONPATH:$BASEDIR 	
python gamelogic/main.py -m DisplayWallTest.json
