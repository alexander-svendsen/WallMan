# -*- coding: utf-8 -*-
import socket


class Server():
    def __init__(self, addr, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((addr, port))
        self.sock.listen(20)
        print "Master waiting for slaves on addr, port:", self.getPortAndAddress()

    def connect(self):
        try:
            (connection, addr) = self.sock.accept()
            print "Client connected", connection, addr  # addr should be a addr, port pair
            return connection, addr
        except Exception as e:
            print "Connection error", e.args

    def close(self, connection):
        connection.close()

    def send(self, connection, data):
        connection.send(data)

    def receive(self, connection, length, timeout=None):
        connection.settimeout(timeout)
        return connection.recv(length)

    def getPortAndAddress(self):
        return self.sock.getsockname()