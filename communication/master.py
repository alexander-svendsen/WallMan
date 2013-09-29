# -*- coding: utf-8 -*-
import socket
import random
import json
import thread
from screenlayout import ScreenLayout
from socketcommunication.server import Server


class Master(Server):
    def __init__(self, addr, port, screen_config, players):
        Server.__init__(self, addr, port)
        self._screen_layout = ScreenLayout(screen_config)
        self._connected_slaves = dict()
        self._players = players

    def listen_for_slaves(self):
        print "Start accepting connections"
        while True:
            connection, address = self.accept_connections()
            self.getSetup(connection, address) #FIXME ?
            thread.start_new(self.reciveDataForEver, (connection, ))

    # FIXME use the revice error to remove disconnected clients
    def reciveDataForEver(self, connection):
        connection.settimeout(None)
        try:
            while True:
                rawData = connection.recv(1024)
                data = json.loads(rawData)
                if data['cmd'] == 'migrate':
                    print "migrate signal recevied", data
                    self._players[data["name"]] = connection
                else:
                    print "Recived somethign strange from the client", data
        except ValueError:
            print "Invalid json recived:", rawData
        except KeyError:
            print "Invalid setup recived", data
        except socket.error:
            print "Connection went down"
        except Exception as e:
            print "Strange exception, time to remove the client from my connections"
            print e

    def getSetup(self, connect, addr, timeout=3):
        connect.settimeout(timeout)
        try:
            rawData = connect.recv(1024)
            data = json.loads(rawData)
            hostname = self._screen_layout.get_id_of_host(data["hostname"])
            if self._screen_layout.is_hostname_valid(hostname):
                self._connected_slaves[hostname] = {"conn": connect, "addr": addr[0], "port": data['port']}
                connect.send(json.dumps({"cmd": "ok"}))
            else:  # Invalid game connected, so send a close signal since it will not be used
                connect.send(json.dumps({"cmd": "close"}))
            print "Connected clients:", self._connected_slaves
            return True
        except socket.timeout:
            print "Timeout: Didn't receive setup from the connection"
        except ValueError:
            print "Invalid json recived:", rawData
        except KeyError:
            print "Invalid setup recived", data
        return False

    def sendOutSetup(self):
        for key, dictValue in self._connected_slaves.iteritems():
            print key
            print '\t Dict:', dictValue
            print '\t Ori :', self._screen_layout.get_connection_setup_for_hostname(key)

            orientation = dict()
            for direction, hostname in self._screen_layout.get_connection_setup_for_hostname(key).iteritems():
                orientation[direction] = (self._connected_slaves[hostname]["addr"], self._connected_slaves[hostname]["port"])
            print "final mix", orientation
            data = {"cmd": "setup", "orientation": orientation}
            dictValue["conn"].send(json.dumps(data))

    def sendToAll(self, data):
        for key, dictValue in self._connected_slaves.iteritems():
            dictValue["conn"].send(data)

    def closeAll(self):
        for key, dictValue in self._connected_slaves.iteritems():
            dictValue["conn"].close()

    def getRandomSocket(self):
        randomKey = random.choice(self._connected_slaves.keys())
        return self._connected_slaves[randomKey]['conn']

    def __len__(self):
        return len(self._connected_slaves)

    def __getitem__(self, key):
        return self._connected_slaves[key]


