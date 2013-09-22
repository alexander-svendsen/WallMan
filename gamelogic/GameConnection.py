# -*- coding: utf-8 -*-
import json
import thread
from socketcommunication import *


class GameConnection():
    def __init__(self, theGame):
        self.theGame = theGame
        self.server = Server('', 0)  # Let the os pick a random port and use localhost
        self.connectedClients = list()  # TODO really a list ?
        self.acceptConnections = True
        self.running = True

    def connectToMaster(self, addr, port):
        self.connection = Client()
        self.connection.connect(addr, port)

    def sendSetup(self):
        self.connection.send(json.dumps({"cmd": "setup",
                                         "hostname": self.connection.getHostName(),
                                         'port': self.server.getPortAndAddress()[1]}))

    def setup(self):
        thread.start_new(self.listenForOtherGames(), ())

    def listenForOtherGames(self):
        while self.acceptConnections:
            connection, addr = self.server.connect()
            self.connectedClients.append(connection)

    def reciveFromAll(self):
        for client in self.connectedClients:
            thread.start_new(self.reciveForEver, (client, 1024))

    def reciveForEver(self, conn, length):
        while self.running:
            conn.recive(length)

    def receiveSetup(self):  #TODO fix execptions
        rawData = self.connection.receive(1024)
        data = json.loads(rawData)
        if data["cmd"] == "close":
            self.theGame.hardQuit()

    def start(self):
        while self.running:
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
                    self.acceptConnections = False
                elif data['cmd'] == "setup":
                    print "yay a connecttion request came from master"
                    print data
                elif data['cmd'] == "close":
                    self.close()

            except Exception as e:
                print "Closing connection to Master, because of an error"
                print e
                self.close()

    def close(self):
        self.running = False
        self.theGame.softQuit()