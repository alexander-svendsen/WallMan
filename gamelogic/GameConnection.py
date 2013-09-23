# -*- coding: utf-8 -*-
import json
import thread
from socketcommunication import *


class GameConnection():
    def __init__(self, theGame):
        self.theGame = theGame
        self.server = Server('', 0)  # Let the os pick a random port and use localhost
        self.connectedClients = list()  # TODO really a list ?

        self.directionConnections = dict()
        self.clientDict = dict()

        self.acceptConnections = True
        self.running = True

    def connectToMaster(self, addr, port):
        self.connection = Client()
        self.connection.connect(addr, port)

    def sendSetup(self):
        self.connection.send(json.dumps({"cmd": "setup",
                                         "hostname": self.connection.getHostName(),
                                         'port': self.server.getPortAndAddress()[1]}))

    def setup(self, masterAddr, masterPort):
        self.connectToMaster(masterAddr, masterPort)
        self.sendSetup()
        self.receiveSetup()

        thread.start_new(self.reciveCommandsFromMaster, ())
        thread.start_new(self.listenForOtherGames, ())

    def listenForOtherGames(self):
        while self.acceptConnections:
            connection, addr = self.server.connect()
            self.connectedClients.append(connection)

    def reciveFromAll(self):
        print self.connectedClients
        for client in self.connectedClients:
            thread.start_new(self.reciveForEver, (client, 1024))

    def reciveForEver(self, conn, length):
        while self.running:
            data = self.server.receive(conn, length)
            self.parseData(data)

    def receiveSetup(self):  #TODO fix execptions
        rawData = self.connection.receive(1024)
        data = json.loads(rawData)
        if data["cmd"] == "close":
            self.theGame.hardQuit()

    def connectToDirection(self, direction, addr):
        addressTuple = addr[0], addr[1]
        if addressTuple in self.clientDict:
            self.directionConnections[direction] = self.clientDict[addressTuple]
        else:
            client = Client()
            self.directionConnections[direction] = client
            self.directionConnections[direction].connect(addr[0], addr[1])
            self.clientDict[addressTuple] = client

    def parseData(self, msg):
        data = json.loads(msg)
        print data
        if data['cmd'] == "join":
            self.theGame.newPlayerJoined(data["name"])

        elif data['cmd'] == "move":
            self.theGame.movePlayer(data["name"], data["direction"])

        elif data['cmd'] == "start":
            self.theGame.start()
            self.acceptConnections = False
            self.reciveFromAll()

        elif data['cmd'] == "setup":
            print data['orientation']
            for key, addr in data['orientation'].iteritems():
                self.connectToDirection(key, addr)
            print "new connections to directions have been established"
            print self.directionConnections

        elif data['cmd'] == "close":
            self.close()

    def reciveCommandsFromMaster(self):
        while self.running:
            try:
                msg = self.connection.receive(1024)
                self.parseData(msg)
            except Exception as e:
                print "Closing connection to Master, because of an error"
                print e
                self.close()

    def close(self):
        self.acceptConnections = False
        self.running = False
        self.theGame.softQuit()