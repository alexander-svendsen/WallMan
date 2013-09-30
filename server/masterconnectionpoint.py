# -*- coding: utf-8 -*-
import functools
import socket
import random
import json
import thread
import screenlayout as sl
import socketcommunication.server as communication


class MasterConnectionPoint(communication.Server):
    def __init__(self, ip, port, screen_config, players):
        communication.Server.__init__(self, ip, port)
        self._screen_layout = sl.ScreenLayout(screen_config)
        self._connected_slaves = dict()
        self._players = players

    def add_player(self, raw):
        data = json.loads(raw)
        game_slave = self._get_random_slave()
        self._players[data["name"]] = game_slave

        data["cmd"] = "join"
        game_slave.send(json.dumps(data))

    def move_player(self, raw):
        data = json.loads(raw)
        if data["name"] in self._players:
            data["cmd"] = "move"
            self._players[data["name"]].send(json.dumps(data))

    def listen_for_slaves(self):
        for connection, address in iter(self.accept_connection,""):
            thread.start_new(self._receive_data_for_ever, (connection, address))

    def _receive_data_for_ever(self, connection, address):
        try:
            for raw in iter(functools.partial(connection.recv,1024), ""):
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
                        connection.send(json.dumps({"cmd": "ok"}))
                    else:  # Invalid game connected, so send a close signal since it will not be used
                        connection.send(json.dumps({"cmd": "close"}))
                        return
                    print "Connected clients:", self._connected_slaves
                else:
                    print "Received something strange from the client", data
        except ValueError:
            print "Invalid json received:", raw
        except KeyError:
            print "Invalid setup received", data
        except socket.error:
            print "Connection went down"
        finally:
            # Know this may cause unintentional error in cases where the hostname isn't received, but it can simply
            # ignore the problem since the it gets run in a thread that completes here anyway and won't cause problem
            # for the rest of the program  # FIXME: IN THE FUTURE
            del self._connected_slaves[hostname]
            self._screen_layout.remove(hostname)

    def send_setup(self):
        for key, value in self._connected_slaves.iteritems():
            print '{0}\n\tDict: {1}\n\tOri : '.format(key, value, self._screen_layout[key])

            connection_config = dict()
            for direction, hostname in self._screen_layout[key].iteritems():
                if hostname not in self._connected_slaves:
                    connection_config[direction] = 'BLOCK'
                    continue

                connection_config[direction] = (self._connected_slaves[hostname]["addr"],
                                                self._connected_slaves[hostname]["port"])
            print "final mix", connection_config
            data = {"cmd": "setup", "connection_config": connection_config}
            value["conn"].send(json.dumps(data))

    def send_to_all(self, data):
        for key, value in self._connected_slaves.iteritems():
            self.send(value["conn"], data)

    def close_all(self):
        for key, value in self._connected_slaves.iteritems():
            self.close(value["conn"])

    def _get_random_slave(self):
        random_key = random.choice(self._connected_slaves.keys())
        return self._connected_slaves[random_key]['conn']

    def __len__(self):
        return len(self._connected_slaves)

    def __getitem__(self, key):
        return self._connected_slaves[key]
