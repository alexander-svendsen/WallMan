# -*- coding: utf-8 -*-
import json
import thread
from socketcommunication import *
import sys, traceback


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
                                         "hostname": self.connection.gethostname,
                                         'port': self.server.getsockname[1]}))

    def setup(self, masterAddr, masterPort):
        self.connectToMaster(masterAddr, masterPort)
        self.sendSetup()
        self.receiveSetup()

        thread.start_new(self.reciveCommandsFromMaster, ())
        thread.start_new(self.listenForOtherGames, ())

    def listenForOtherGames(self):
        while self.acceptConnections:
            connection, addr = self.server.accept_connection()
            self.connectedClients.append(connection)

    def reciveFromAll(self):
        print self.connectedClients
        for client in self.connectedClients:
            thread.start_new(self.reciveForEver, (client, 1024))

    def reciveForEver(self, conn, length):
        try:
            while self.running:
                data = self.server.receive(conn, length)  # FIXME uses master connection to recive ?
                print "Client data"
                self.parseData(data)
        except Exception as e:
            print type(e)
            traceback.print_exc(file=sys.stdout)
            raise

    def receiveSetup(self):  # TODO fix execptions
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

    #REVIEW: OBVIOUSLY
    def sendPlayerInDirection(self, **kwargs):
        self.directionConnections[kwargs["current_direction"]].send(
            json.dumps({'cmd': 'migrate',
                        'direction': kwargs["current_direction"],
                        'name': kwargs["name"],
                        'x': kwargs["layout_x"],
                        'y': kwargs["layout_y"],
                        'newDirection': kwargs["new_direction"],
                        'color': kwargs["color"],
                        'askii': kwargs["askii"],
                        'askii-color': kwargs["askii_color"]}))

    #REVIEW
    def parseData(self, msg):
        data = json.loads(msg)
        print "\tRecived data:", data
        if data['cmd'] == "join":
            self.theGame.newPlayerJoined(data["name"])

        elif data['cmd'] == "move":
            self.theGame.movePlayer(data["name"], data["direction"])

        elif data['cmd'] == "start":
            self.theGame.start()
            self.acceptConnections = False
            self.reciveFromAll()

        elif data['cmd'] == "setup":
            print data['connection_config']
            for key, addr in data['connection_config'].iteritems():
                self.connectToDirection(key, addr)
            print "new connections to directions have been established"
            print self.directionConnections
            self.theGame.update_players_migrations()

        elif data['cmd'] == "close":
            self.close()

        elif data['cmd'] == "migrate":
            self.theGame.migratePlayer(data["name"], data["direction"], data["newDirection"], data["x"], data["y"], data["color"], data["askii"], data["askii-color"])
            self.connection.send(json.dumps({'cmd': 'migrate', 'name': data["name"]}))

        else:
            print "Strange cmd recived", data

    def reciveCommandsFromMaster(self):
        while self.running:
            try:
                msg = self.connection.receive(1024)
                print "Data from master"
                self.parseData(msg)
            except Exception as e:
                print "Closing connection to Master"
                print "Error:", type(e), e
                traceback.print_exc(file=sys.stdout)
                self.close()
                raise

    def close(self):
        self.acceptConnections = False
        self.running = False
        for client in self.connectedClients:
            self.server.close(client)
        self.connection.close()

        for client in self.clientDict.values():
            client.close()

        self.theGame.softQuit()