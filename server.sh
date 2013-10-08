#!/bin/bash
# Shellscript for running the server for linux users

BASEDIR=..
export PYTHONPATH=$PYTHONPATH:$BASEDIR
cd server # Must be inside this directory to get static to work
python server.py -sc BigDisplayWall.json
