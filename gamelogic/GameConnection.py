# -*- coding: utf-8 -*-
from functools import partial
import json
import thread
import threading
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

    #review a good time?
    def periodic_send_status(self, time=10):
        threading.Timer(time, partial(self.periodic_send_status, time)).start()
        self.send_status_data()

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
            thread.start_new(self.reciveForEver, (connection, 1024))

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
        elif data["cmd"] == "setup":
            self.theGame.map = data["map"]

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
                        'sprite_x': kwargs["sprite_x"],
                        'sprite_y': kwargs["sprite_y"],
                        'speed_level': kwargs["speed_level"]}))

    #REVIEW
    def parseData(self, msg):
        print "\tRecived data:", msg
        list_msg = msg.split('\n')
        for data_entry in list_msg:
            if not len(data_entry):
                continue
            data = json.loads(data_entry)
            if data['cmd'] == "join":
                self.theGame.newPlayerJoined(data["name"])

            elif data['cmd'] == "move":
                self.theGame.movePlayer(data["name"], data["direction"])

            elif data['cmd'] == "start":
                self.theGame.start()
                self.periodic_send_status()

            elif data['cmd'] == "setup":
                print data['connection_config']
                for key, addr in data['connection_config'].iteritems():
                    if addr != 'BLOCK':  # TODO: should do something about this direction
                        self.connectToDirection(key, addr)
                self.theGame.update_players_migrations()

            elif data['cmd'] == "close":
                self.send_status_data()
                self.close()

            elif data['cmd'] == "status":
                self.send_status_data()

            elif data['cmd'] == "migrate":
                self.theGame.migratePlayer(data["name"], data["direction"], data["newDirection"], data["x"], data["y"], data["color"], data["sprite_x"], data["sprite_y"], data["speed_level"])
                self.connection.send(json.dumps({'cmd': 'migrate', 'name': data["name"]}))

            elif data['cmd'] == "flash":
                self.theGame.flash_player(data["name"])
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
                traceback.print_exc(file=sys.stdout)  # TODO remove
                self.close()
                raise

    def send_status_data(self):
        raw_data = {'cmd': 'status', 'score': self.theGame.get_tiles()}
        data = json.dumps(raw_data)
        self.connection.send(data)

    def close(self):
        self.acceptConnections = False
        self.running = False
        for client in self.connectedClients:
            self.server.close(client)
        self.connection.close()

        for client in self.clientDict.values():
            client.close()

        self.theGame.softQuit()