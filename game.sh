#!/bin/bash
# My first script
# Shellscript for runnning the game for linux users

BASEDIR=$(cd $(dirname $0); pwd)

cd $BASEDIR
export PYTHONPATH=$PYTHONPATH:$BASEDIR

#change the python file arguments if you wish to change some configuration
python game/main.py -r 504 504
