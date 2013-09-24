# -*- coding: utf-8 -*-
import socket
import random
import json
import screenlayout
from socketcommunication.server import Server
import thread

#TODO THINK ABOUT IF I WANT INHERENTENCE AT ALL
class Master(Server):
    def __init__(self, addr, port, orientation, players):
        Server.__init__(self, addr, port)
        self.orientation = screenlayout.ScreenLayout(orientation)
        self.connections = dict()

        #FIXME... refactor
        self.players = players

    def listen(self):
        print "Start accepting connections"
        while True:
            connection, addr = self.connect()
            self.getSetup(connection, addr) #FIXME ?
            thread.start_new(self.reciveDataForEver, (connection, ))

    # FIXME use the revice error to remove disconnected clients
    def reciveDataForEver(self, connection):
        connection.settimeout(None)
        try:
            rawData = connection.recv(1024)
            data = json.loads(rawData)
            if data['cmd'] == 'migrate':
                print "migrate signal recevied", data
                self.players[data["name"]] = connection
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
            hostname = self.orientation.getIdOfHost(data["hostname"])
            if self.orientation.isNameValid(hostname):
                self.connections[hostname] = {"conn": connect, "addr": addr[0], "port": data['port']}
                connect.send(json.dumps({"cmd": "ok"}))
            else:  # Invalid game connected, so send a close signal since it will not be used
                connect.send(json.dumps({"cmd": "close"}))
            print "Connected clients:", self.connections
            return True
        except socket.timeout:
            print "Timeout: Didn't receive setup from the connection"
        except ValueError:
            print "Invalid json recived:", rawData
        except KeyError:
            print "Invalid setup recived", data
        return False

    def sendOutSetup(self):
        for key, dictValue in self.connections.iteritems():
            print key
            print '\t Dict:', dictValue
            print '\t Ori :', self.orientation.getConnectionSetupForId(key)

            orientation = dict()
            for direction, hostname in self.orientation.getConnectionSetupForId(key).iteritems():
                orientation[direction] = (self.connections[hostname]["addr"], self.connections[hostname]["port"])
            print "final mix", orientation
            data = {"cmd": "setup", "orientation": orientation}
            dictValue["conn"].send(json.dumps(data))

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


