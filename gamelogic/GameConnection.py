# -*- coding: utf-8 -*-
import json
import sys
import time
from gamelogic.Slave import Slave


class GameConnection():
    def __init__(self, theGame):
        self.theGame = theGame

    def connectToMaster(self, addr, port):
        self.connection = Slave()
        self.connection.connect(addr, port)

    def sendSetup(self):  # Todo more setup do here
        self.connection.send(json.dumps({"cmd": "setup", "hostname": self.connection.getHostName()}))

    def receiveSetup(self):  #TODO fix execptions
        rawData = self.connection.receive(1024)
        data = json.loads(rawData)
        if data["cmd"] == "close":
            self.theGame.hardQuit()

    def start(self):
        while True:
            try:
                msg = self.connection.receive(1024)
                data = json.loads(msg)
                print data
                if data['cmd'] == "join":
                    print "new player joining"
                    self.theGame.newPlayerJoined(data["name"])
                elif data['cmd'] == "move":
                    self.theGame.movePlayer(data["name"], data["direction"])
                elif data['cmd'] == "start":
                    self.theGame.start()
                elif data['cmd'] == "close":
                    self.close()

            except Exception as e:
                print "Closing connection to Master"
                print e
                self.close()

    def close(self):
        self.theGame.softQuit()