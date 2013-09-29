# -*- coding: utf-8 -*-
import socket
import random
import json
import thread

from screenlayout import ScreenLayout
from socketcommunication.server import Server


class Master(Server):
    def __init__(self, ip, port, screen_config, players):
        Server.__init__(self, ip, port)
        self._screen_layout = ScreenLayout(screen_config)
        self._connected_slaves = dict()
        self._players = players
        self._run = True  # TODO: Actually set it false sometime

    def listen_for_slaves(self):
        print "Start accepting connections"
        while True:
            connection, address = self.accept_connection()
            thread.start_new(self.receive_data_for_ever, (connection, address))

    # FIXME use the receive error to remove disconnected clients
    def receive_data_for_ever(self, connection, address):
        connection.settimeout(None)
        try:
            while self._run:
                raw = connection.recv(1024)
                data = json.loads(raw)
                if data['cmd'] == 'migrate':
                    print "migrate signal received", data
                    self._players[data["name"]] = connection
                elif data['cmd'] == 'setup':
                    hostname = self._screen_layout.get_id_of_host(data["hostname"])
                    if self._screen_layout.is_hostname_valid(hostname):
                        self._connected_slaves[hostname] = {"conn": connection,
                                                            "addr": address[0],
                                                            "port": data['port']}
                        connection.send(json.dumps({"cmd": "ok"}))  #FIXME do i actually need to send anything?
                    else:  # Invalid game connected, so send a close signal since it will not be used
                        connection.send(json.dumps({"cmd": "close"}))
                    print "Connected clients:", self._connected_slaves
                else:
                    print "Received something strange from the client", data
        except ValueError:
            print "Invalid json received:", raw
        except KeyError:
            print "Invalid setup received", data
        except socket.error:
            print "Connection went down"
        except Exception:
            print "Strange exception, time to remove the client from my connections"
            raise  # TODO: what it said in the connection

    def send_setup(self):
        for key, value in self._connected_slaves.iteritems():
            print '{0}\n\tDict: {1}\n\tOri : '.format(key, value, self._screen_layout.get_setup_for_hostname(key))

            connection_config = dict()
            for direction, hostname in self._screen_layout.get_setup_for_hostname(key).iteritems():
                connection_config[direction] = (self._connected_slaves[hostname]["addr"],
                                                self._connected_slaves[hostname]["port"])
            print "final mix", connection_config
            data = {"cmd": "setup", "orientation": connection_config}  #Fixme Orientation ? rename
            value["conn"].send(json.dumps(data))

    def send_to_all(self, data):
        for key, value in self._connected_slaves.iteritems():
            self.send(value["conn"], data)

    def close_all(self):
        for key, value in self._connected_slaves.iteritems():
            self.close(value["conn"])

    def get_random_slave(self):
        random_key = random.choice(self._connected_slaves.keys())
        return self._connected_slaves[random_key]['conn']

    def __len__(self):
        return len(self._connected_slaves)

    def __getitem__(self, key):
        return self._connected_slaves[key]

if __name__ == "__main__":
    #TODO Actually test things here
    pass