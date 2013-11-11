#!/bin/bash
# Shellscript for runnning the game for linux users

BASEDIR=$(cd $(dirname $0); pwd)  # To make it dynamicly enough for the cluster fork command
export PYTHONPATH=$PYTHONPATH:$BASEDIR
cd $BASEDIR
python gamelogic/main.py
