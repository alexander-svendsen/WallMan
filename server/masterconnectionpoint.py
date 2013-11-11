# -*- coding: utf-8 -*-
import functools
import socket
import random
import json
import thread
import threading
import time
from collections import defaultdict
import socketcommunication as communication
from screenlayout import ScreenLayout


class MasterConnectionPoint(communication.Server):
    """
    The master server. Handles everything when it comes to the game screens
    """
    def __init__(self, ip, port, screen_config, timer):
        communication.Server.__init__(self, ip, port)
        print "Master Connection point established at: {0}:{1}".format(ip, port)

        self._screen_layout = ScreenLayout(screen_config)
        self._connected_slaves = {}
        self._players = {}
        self._player_score = defaultdict(lambda: 0)
        self._conn_to_player_dict = defaultdict(lambda: list())

        self._shutdown_dict = {}

        self.timer = timer
        self._start_time = None
        self._end_time = None
        self.start = False
        self.shutdown = 0

    def add_player(self, raw_data):
        """
        Method for adding a new player into the game. Picks a random connected game and adds the player to that one
        :param raw_data: json string data. Must at look like: "{'name': <username>}"
        :return:
        """
        data = json.loads(raw_data)
        if not self._connected_slaves:  # Error testing
            return
        if data["name"] in self._players:  # Should not rejoin a player
            return  # review Error support

        game_slave = self._get_random_slave()
        self._players[data["name"]] = game_slave
        self._conn_to_player_dict[game_slave].append(data["name"])

        data["cmd"] = "join"
        game_slave.send(json.dumps(data) + '\n')

    def move_player(self, raw_data):
        """
        Method for moving the specified player. Doesn't really matter if the player isn't in the game.
        :param raw_data: json string data. Must look like: "{'name': <username> }"
        """
        print raw_data
        print  self._players
        data = json.loads(raw_data)
        if data["name"] in self._players:
            data["cmd"] = "move"
            self._players[data["name"]].send(json.dumps(data) + '\n')

    def listen_for_slaves(self):
        """
        Method to make the master start listening for new games connecting. Starts automatically receiving data from the
        clients until the game ends, or is told otherwise. Different actions are executed based on the recived data.

        Although they are connected and the master receives data from the client, nothing really happens before the
        client sends the proper setup to the master.
        """
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
                    self._conn_to_player_dict[connection].append(data["name"])
                    self._players[data["name"]] = connection

                elif data['cmd'] == 'setup':
                    hostname = self._screen_layout.get_id_of_host(data["hostname"])
                    if self._screen_layout.is_hostname_valid(hostname):
                        self._connected_slaves[hostname] = {"conn": connection,
                                                            "addr": address[0],
                                                            "port": data['port'],
                                                            "score": {}}
                        print self._screen_layout[hostname]
                        connection.send(json.dumps({"cmd": "setup",
                                                    "map": self._screen_layout.get_map_for_hostname(hostname)}))
                    else:  # Invalid game connected, so send a close signal since it will not be used
                        print "Invalid host connected"
                        connection.send(json.dumps({"cmd": "close"}))
                        return
                    print "Connected clients:", self._connected_slaves

                elif data['cmd'] == "status":
                    self._connected_slaves[hostname]["score"] = data['score']

                    if self.shutdown:
                        self._shutdown_dict[connection] = 1  # Uses dict to ensure uniqueness of the signal
                        if len(self._shutdown_dict) == self.shutdown:
                            self._player_score.clear()
                            self._calculate_score()
                            print self._player_score
                else:
                    print "Received something strange from the client", data
        except ValueError:
            print "Invalid json data received:", raw
        except KeyError:
            print "Invalid json received, KeyError", data
        except socket.error:
            print "Connection went down"
        finally:  # remove the game and all it's associated data
            if hostname not in self._connected_slaves:
                return

            for name in self._conn_to_player_dict[self._connected_slaves[hostname]['conn']]:
                self._fix_player(name)
            del self._conn_to_player_dict[self._connected_slaves[hostname]['conn']]
            self._connected_slaves[hostname]['conn'].close()
            del self._connected_slaves[hostname]
            self._screen_layout.remove(hostname)
            print "Clients left connected: ", self._connected_slaves

    def flash_player(self, raw_data):
        """
        Sends a flash signal to the game machine responsible for the client
        :param raw_data: json string data. Must look like "{'name': <username>}"
        """
        json_data = json.loads(raw_data)
        player_name = json_data["name"]
        if player_name in self._players:
            json_data["cmd"] = "flash"
            self._players[player_name].send(json.dumps(json_data) + '\n')

    # review should be an other solution
    def _fix_player(self, name):
        del self._players[name]

    def get_status(self):
        """
        Returns the current stored player score and how much time there is left of the game. The score system is
        asynchronous, so it may not be up to date, but will be so at the end of the game session
        :return:
        """
        time_since_beginning = self.timer
        if self._start_time and self.start:
            time_since_beginning = int(self.timer - (time.time() - self._start_time))
        status = {"started": self.start, "score": {}, "time_left": time_since_beginning}
        if self.shutdown:  # No point calculating anything since the game has ended
            status["score"] = self._player_score
        else:
            self._player_score.clear()
            status["score"] = self._calculate_score()
        return status

    def _calculate_score(self):
        for item in self._connected_slaves.itervalues():
            for name, score in item["score"].iteritems():
                self._player_score[name] += score  # FIXME NOT ATOMIC CAN BE WRONG. FIX
        return self._player_score

    def shutdown_clients(self):
        """
        Closes all the connected games and calculates the scores
        """
        self.start = False
        self.shutdown = len(self._connected_slaves)
        self._send_to_all(json.dumps({"cmd": "close"}))

    def start_game(self):
        """
        Starts the game. Sends a start signal to all the connected clients
        """
        self.start = True
        self.shutdown = False  # Can refresh the game now again
        self._send_to_all(json.dumps({"cmd": "start"}))
        if self.timer:  # A timer for how long until the game ends
            self._start_time = time.time()
            threading.Timer(self.timer, self.shutdown_clients).start()

    def send_setup(self):
        """
        Sends the current connection setup to all the clients. Who they should connect to and such
        """
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

    def _send_to_all(self, data):
        for key, value in self._connected_slaves.iteritems():
            self.send(value["conn"], data)

    def _get_random_slave(self):
        random_key = random.choice(self._connected_slaves.keys())
        return self._connected_slaves[random_key]['conn']

    def __len__(self):
        return len(self._connected_slaves)

    def __getitem__(self, key):
        return self._connected_slaves[key]
