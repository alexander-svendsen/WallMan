#!/bin/bash
# Shellscript for runnning the game for linux users

BASEDIR=$(cd $(dirname $0); pwd)
export PYTHONPATH=$PYTHONPATH:$BASEDIR
cd $BASEDIR
python gamelogic/main.py -m DisplayWallTest.json
