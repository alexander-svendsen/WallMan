#!/bin/bash
# My first script
BASEDIR=$(dirname $BASH_SOURCE )

export PYTHONPATH=$PYTHONPATH:$BASEDIR 	
python gamelogic/main.py -m DisplayWallTest.json
