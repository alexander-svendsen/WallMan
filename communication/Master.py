# -*- coding: utf-8 -*-
import socket
import random
import json
import screenlayout


class Master():
    def __init__(self, addr, port, orientation):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print "Master waiting for slaves on addr, port:", addr, port
        self.sock.bind((addr, port))
        self.sock.listen(4)

        self.orientation = screenlayout.ScreenLayout(orientation)
        self.connections = dict()

    def connect(self):
        print "Start accepting connections"
        while True:
            try:
                (connection, addr) = self.sock.accept()
                print "Client connected", connection, addr  # addr should be a addr, port pair
                self.getSetup(connection)
            except Exception as e:
                print "Connection error", e.args

    def getSetup(self, connect, timeout=3):
        connect.settimeout(timeout)
        try:
            rawData = connect.recv(1024)
            data = json.loads(rawData)
            hostname = self.orientation.getIdOfHost(data["hostname"])
            if self.orientation.isNameValid(hostname):
                self.connections[hostname] = {"conn": connect, "addr": "TODO"}
                connect.send(json.dumps({"cmd": "ok"}))
            else:  # Invalid slave connected, so send a close signal since it will not be used
                connect.send(json.dumps({"cmd": "close"}))

            print self.connections
            return True
        except socket.timeout:
            print "Timeout: Didn't receive setup from the connection"
        except ValueError:
            print "Invalid json recived:", rawData
        except KeyError:
            print "Invalid setup recived", data
        return False

    def sendToAll(self, data):
        for key, dictValue in self.connections.iteritems():
            dictValue["conn"].send(data)

    def closeAll(self):
        for key, dictValue in self.connections.iteritems():
            dictValue["conn"].close()

    def getRandomSocket(self):
        randomKey = random.choice(self.connections.keys())
        return self.connections[randomKey]['conn']

    def __len__(self):
        return len(self.connections)

    def __getitem__(self, key):
        return self.connections[key]


