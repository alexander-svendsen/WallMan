# -*- coding: utf-8 -*-
import socket


class Server():
    def __init__(self, addr, port):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((addr, port))
        self._sock.listen(20)
        # print "Server listening on addr, port:", self.get_port_and_address() Maybe log instead

    def accept_connection(self):
        return self._sock.accept()

    def close(self, connection):
        connection.close()

    def send(self, connection, data):
        connection.send(data)

    def receive(self, connection, length, timeout=None):
        connection.settimeout(timeout)
        return connection.recv(length)

    def get_port_and_address(self):
        return self._sock.getsockname()