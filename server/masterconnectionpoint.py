# -*- coding: utf-8 -*-
from collections import defaultdict
import functools
import socket
import random
import json
import thread
import threading
from functools import partial
import screenlayout as sl
import socketcommunication as communication


class MasterConnectionPoint(communication.Server):
    def __init__(self, ip, port, screen_config, timer):
        communication.Server.__init__(self, ip, port)
        print "Master Connection point established at: {0}:{1}".format(ip, port)
        self._screen_layout = sl.ScreenLayout(screen_config)
        self._connected_slaves = dict()
        self._players = dict()
        self._player_score = defaultdict(lambda: 0)
        self._conn_to_player_dict = defaultdict(lambda: list())
        self.shutdown = False
        self._shutdown_dict = dict()
        self.timer = timer

    def add_player(self, raw):
        data = json.loads(raw)
        if not self._connected_slaves:  # Error testing
            return
        if data["name"] in self._players:  # Should not rejoin a player
            return  # review Error support

        game_slave = self._get_random_slave()
        self._players[data["name"]] = game_slave
        self._conn_to_player_dict[game_slave].append(data["name"])

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
        hostname = ""
        try:
            for raw in iter(functools.partial(connection.recv,1024), ""):
                data = json.loads(raw)
                if data['cmd'] == 'migrate':
                    print "migrate signal received", data
                    self._conn_to_player_dict[self._players[data["name"]]].remove(data["name"])
                    self._players[data["name"]] = connection
                    self._conn_to_player_dict[connection].append(data["name"])
                elif data['cmd'] == 'setup':
                    hostname = self._screen_layout.get_id_of_host(data["hostname"])
                    if self._screen_layout.is_hostname_valid(hostname):
                        self._connected_slaves[hostname] = {"conn": connection,
                                                            "addr": address[0],
                                                            "port": data['port']}
                        connection.send(json.dumps({"cmd": "ok"}))
                    else:  # Invalid game connected, so send a close signal since it will not be used
                        print "Invalid host connected"
                        connection.send(json.dumps({"cmd": "close"}))
                        return
                    print "Connected clients:", self._connected_slaves
                elif data['cmd'] == "status":
                    for name, score in data['score'].iteritems():
                        self._player_score[name] += score
                    if self.shutdown:
                        self._shutdown_dict[connection] = 1  # Uses dict to ensure uniqueness of the signal
                        if len(self._shutdown_dict) == self.waiting_len:  # FIXME, what if conn has gone down? here i simply don't care about them
                            print "FINAL SCORE:", self._player_score
                            self._player_score.clear()
                            self.shutdown = False
                            self._shutdown_dict.clear()
                else:
                    print "Received something strange from the client", data
        except ValueError:
            print "Invalid json data received:", raw
        except KeyError:
            print "Invalid json received, KeyError", data
        except socket.error:
            print "Connection went down"
        finally:
            if hostname not in self._connected_slaves:
                return

            for name in self._conn_to_player_dict[self._connected_slaves[hostname]['conn']]:
                self.fix_player(name)

            del self._conn_to_player_dict[self._connected_slaves[hostname]['conn']]
            del self._connected_slaves[hostname]
            self._screen_layout.remove(hostname)

    # review should be an other solution
    def fix_player(self, name):
        del self._players[name]

    def shutdown_clients(self):
        self.send_to_all(json.dumps({"cmd": "close"}))
        # FIXME, what if conn has gone down? here i simply don't care about them
        self.waiting_len = len(self._connected_slaves)
        if self.waiting_len:
            self.shutdown = True

    def start_game(self):
        self.send_to_all(json.dumps({"cmd": "start"}))
        if self.timer:
            threading.Timer(self.timer, partial(self.send_to_all, (json.dumps({"cmd": "close"})))).start()

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
