#!/bin/bash
# Shellscript for running the server

BASEDIR=..
export PYTHONPATH=$PYTHONPATH:$BASEDIR
cd server # Must be inside this directory to get static to work	
python server.py
