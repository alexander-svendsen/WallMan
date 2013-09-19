# -*- coding: utf-8 -*-
import socket


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