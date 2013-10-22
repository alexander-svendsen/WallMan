# -*- coding: utf-8 -*-
from collections import defaultdict
import functools
import socket
import random
import json
import thread
import threading
import screenlayout as sl
import socketcommunication as communication
import time


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
        self._start_time = None
        self._end_time = None
        self.start = False

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
        game_slave.send(json.dumps(data) + '\n')

    def move_player(self, raw):
        data = json.loads(raw)
        if data["name"] in self._players:
            data["cmd"] = "move"
            self._players[data["name"]].send(json.dumps(data) + '\n')

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
                                                            "port": data['port'],
                                                            "score": dict()}
                        connection.send(json.dumps({"cmd": "ok"}))
                    else:  # Invalid game connected, so send a close signal since it will not be used
                        print "Invalid host connected"
                        connection.send(json.dumps({"cmd": "close"}))
                        return
                    print "Connected clients:", self._connected_slaves
                elif data['cmd'] == "status":
                    self._connected_slaves[hostname]["score"] = data['score']

                    if self.shutdown:
                        self._shutdown_dict[connection] = 1  # Uses dict to ensure uniqueness of the signal
                        # FIXME, what if conn has gone down? here i simply don't care about them
                        if len(self._shutdown_dict) == len(self._connected_slaves):
                            self._player_score.clear()
                            self.calculate_score()
                            print self._player_score
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

    def flash_player(self, data):
        json_data = json.loads(data)
        player_name = json_data["name"]
        if player_name in self._players:
            json_data["cmd"] = "flash"
            self._players[player_name].send(json.dumps(json_data) + '\n')

    # review should be an other solution
    def fix_player(self, name):
        del self._players[name]

    def get_status(self):
        time_since_beginning = self.timer
        if self._start_time and self.start:
            time_since_beginning = int(self.timer - (time.clock() - self._start_time))
        status = {"started": self.start, "score": {}, "time_left": time_since_beginning}
        if self.shutdown:  # No point calculating anything since the game has ended
            status["score"] = self._player_score
        else:
            self._player_score.clear()
            status["score"] = self.calculate_score()
        return status

    def calculate_score(self):
        for item in self._connected_slaves.itervalues():
            for name, score in item["score"].iteritems():
                self._player_score[name] += score  # TODO NOT ATOMIC CAN BE WRONG. FIX
        return self._player_score

    def shutdown_clients(self):
        self.start = False
        self.send_to_all(json.dumps({"cmd": "close"}))
        # FIXME, calc final score
        if len(self._connected_slaves):
            self.shutdown = True

    def start_game(self):
        self.start = True
        self.shutdown = False  # Can refresh the game now again
        self.send_to_all(json.dumps({"cmd": "start"}))
        if self.timer:
            self._start_time = time.clock()
            threading.Timer(self.timer, self.shutdown_clients).start()

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
