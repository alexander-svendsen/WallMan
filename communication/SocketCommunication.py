# -*- coding: utf-8 -*-
import socket
import random


class Master():
    def __init__(self, addr, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        print "Master waiting for slaves on addr, port:", addr, port
        self.sock.bind((addr, port))
        self.sock.listen(4)
        self.connections = dict()

    def connect(self):
        print "Start accepting connections"
        while True:
            try:
                (connection, addr) = self.sock.accept()
                print "Client connected", connection, addr  # addr should be a addr, port pair
                self.connections[addr] = connection  #Does it really need to be a dict ?
            except Exception as e:
                print "Connection error", e.args

    def receiveFromAll(self, length, timeout=None):
        for connection in self.connections.values():
            connection.settimeout(timeout)
            connection.recv(length)  # Well need to do something about this

    def sendToAll(self, data):
        for connection in self.connections.values():
            connection.send(data)

    def closeAll(self):
        for connection in self.connections.values():
            connection.close()

    def getRandomSocket(self):
        return random.choice(self.connections.values())

    def __len__(self):
        return len(self.connections)

    def __getitem__(self, key):
        return self.connections[key]


class Slave():
    def connect(self, addr, port):
        print "Client connecting to: ", addr, port
        self.cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cs.connect((addr, port))
        print "Connection complete"

    def close(self):
        self.cs.close()

    def send(self, data):
        self.cs.send(data)

    def receive(self, length, timeout=None):
        self.cs.settimeout(timeout)
        return self.cs.recv(length)