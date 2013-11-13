# -*- coding: utf-8 -*-
import socket


class Client():
    def __init__(self):
        self.cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, addr, port, timeout=None):
        print "Client connecting to: ", addr, port
        self.cs.settimeout(timeout)
        self.cs.connect((addr, port))

    def close(self):
        self.cs.close()

    def send(self, data):
        self.cs.send(data)

    def receive(self, length, timeout=None):
        self.cs.settimeout(timeout)
        return self.cs.recv(length)

    def getsockname(self):
        return self.cs.getsockname()

    @property
    def connection(self):
        return self.cs

    @property
    def gethostname(self):
        return socket.gethostname()