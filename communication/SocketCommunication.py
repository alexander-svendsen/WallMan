# -*- coding: utf-8 -*-
import socket

#TODO Refactor out the dictonary part, should be more dynmaic then this
class Server():
    def __init__(self, addr, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        print "server listening on addr, port: ", addr, port
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

    def receive(self, length, timeout=None):  # TODO: FIX IT
        for connection in self.connections.values():
            connection.settimeout(timeout)
            connection.recv(length)  # Well need to do something about this

    def send(self, data):  # TODO: FIX IT
        for connection in self.connections.values():
            connection.send(data)

    def close(self):
        for connection in self.connections.values():
            connection.close()


class Client():
    def connect(self, addr, port):
        print "Client connecting to: ", addr,port
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