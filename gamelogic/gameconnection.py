# -*- coding: utf-8 -*-
import json
import thread
import threading
import sys
import traceback
from collections import defaultdict
from functools import partial
from socketcommunication import *

OPPOSITE_DIRECTION_DICT = {"left": "right", "right": "left", "up": "down", "down": "up"}


class GameConnection():
    """
    Class to handle all the necessary connections.
    """

    def __init__(self, the_game):
        self.the_game = the_game
        self.server = Server('', 0)  # Let the os pick a random port and use localhost
        self.accept_connections = True  # Bool if the game should still accept connections
        self.running = True  # Bool to tell the threads to stop running when the game ends

        # A list of connected clients. Using it to know who to disconnect to, when shutting down
        self.connected_clients = []

        # A dict over which direction and which connection in that direction to use
        self.direction_connection_dict = {}
        # The connection can have multiple directions therefore the defaultdict(list)
        self.connection_direction_dict = defaultdict(list)

        # A list over the directions the game is waiting to be connected to. If there is directions in the list when
        # the game starts, it means something wrong happened to the client in that direction therefor the path
        # to that client is blocked
        self.wait_list = []

    def _periodic_send_status(self, time=10):
        self.send_status_data()
        threading.Timer(time, partial(self._periodic_send_status, time)).start()

    def _connect_to_master(self, addr, port):
        self.connection = Client()
        self.connection.connect(addr, port, 5)

    def _send_setup(self):
        self.connection.send(json.dumps({"cmd": "setup",
                                         "hostname": self.connection.gethostname,
                                         'port': self.server.getsockname[1]}))

    def setup(self, master_address, master_port):
        """
        Setup to start the game connection. Must be called for everything to be started and for the game to know where
        to connect to the master. Should be the first thing called when using this object

        :param master_address: address to connect to the master
        :param master_port: port to connect to the master
        """
        self._connect_to_master(master_address, master_port)
        self._send_setup()
        self._receive_setup()

        thread.start_new(self._receive_commands_from_master, ())
        thread.start_new(self._listen_for_other_games, ())

    def _listen_for_other_games(self):
        while self.accept_connections:
            connection, address = self.server.accept_connection()
            print "Game connected on", connection, address
            self.connected_clients.append(connection)
            thread.start_new(self._receive_for_ever, (connection, 1024))

    def _receive_for_ever(self, conn, length):
        try:
            while self.running:
                data = conn.recv(length)
                if data == 0 or data == '':  # The python program crashed
                    raise socket.error
                print "Client data"
                self._parse_data(conn, data)
        except socket.error:
            print "Lost connection to the:", self.connection_direction_dict[conn]
            for direction in self.connection_direction_dict[conn]:  # Blocks the path in the faulty direction
                self.the_game.blockPathsInDirection(direction)
            self.the_game.redrawGameLayout()
        except Exception as e:  # To see the rest of the exceptions if any
            print "Error:", type(e), e
            traceback.print_exc(file=sys.stdout)
            raise

    def _receive_setup(self):
        rawData = self.connection.receive(1024)
        if rawData == 0 or rawData == '':  # The python program crashed
            raise socket.error

        data = json.loads(rawData)
        if data["cmd"] == "close":
            self.the_game.hardQuit()
        elif data["cmd"] == "setup":
            self.the_game.map = data["map"]
        else:
            print "Strange setup from master", data

    def send_player_in_direction(self, **kwargs):
        """
        Method to migrate players to another game client.
        :param kwargs: parameters to send to the other game client
        """
        self.direction_connection_dict[kwargs["current_direction"]].send(
            json.dumps({'cmd': 'migrate',
                        'direction': kwargs["current_direction"],
                        'name': kwargs["name"],
                        'x': kwargs["layout_x"],
                        'y': kwargs["layout_y"],
                        'newDirection': kwargs["new_direction"],
                        'color': kwargs["color"],
                        'sprite_x': kwargs["sprite_x"],
                        'sprite_y': kwargs["sprite_y"],
                        'speed_level': kwargs["speed_level"]}))

    def _connect_to_client(self, connection_ip, connection_port, direction_list):
        client = Client()
        try:
            send_list = []  # A list to store which direction this connection represent to the other client
            client.connect(connection_ip, connection_port)

            for direction in direction_list:
                self.direction_connection_dict[direction] = client  # storing the client to the direction
                send_list.append(OPPOSITE_DIRECTION_DICT[direction])  # opposite direction to the ones this game uses

            # storing the direction to the client
            self.connection_direction_dict[client.connection].extend(direction_list)
            self.connected_clients.append(client.connection)

            client.send(json.dumps({'cmd': 'setup_migration_direction', "direction": send_list}))
            thread.start_new(self._receive_for_ever, (client.connection, 1024))

        except socket.error:
            # could not connect to direction so should block it
            for direction in direction_list:
                self.the_game.blockPathsInDirection(direction)
                if direction in self.direction_connection_dict:
                    del self.direction_connection_dict[direction]
            if client.connection in self.connection_direction_dict:
                del self.connection_direction_dict[client.connection]
            if client.connection in self.connected_clients:
                self.connected_clients.remove(client.connection)

    def _connect_to_direction(self, address, direction_list):
        my_ip = self.connection.getsockname()[0]
        my_port = self.server.getsockname[1]
        connection_ip, connection_port = address

        # comparing ip as strings, as long as python always agree with itself what is bigger
        # there i no need to bother calculate and compare anything ourselves
        if connection_ip < my_ip:
            self._connect_to_client(connection_ip, connection_port, direction_list)
            return
        elif connection_ip == my_ip:  # need to compare using ip instead, they can never be equal
            if connection_port < my_port:
                self._connect_to_client(connection_ip, connection_port, direction_list)
                return

        # Appends the direction to the wait list, to know if something hasn't connected
        for direction in direction_list:
            self.wait_list.append(direction)

    def _parse_data(self, conn, msg):
        print "\tRecived data:", msg
        list_msg = msg.split('\n')  # In cases where there is multiple msg bottled together
        for data_entry in list_msg:
            if not len(data_entry):
                continue

            data = json.loads(data_entry)

            if data['cmd'] == 'join':
                self.the_game.newPlayerJoined(data['name'])

            elif data['cmd'] == 'setup_migration_direction':
                for direction in data['direction']:
                    self.direction_connection_dict[direction] = conn
                    if direction in self.wait_list:  # In those cases where its quicker to connect then i am to add it
                        self.wait_list.remove(direction)
                self.connection_direction_dict[conn].extend(data['direction'])
                self.the_game.update_players_migrations()

            elif data['cmd'] == 'move':
                self.the_game.movePlayer(data['name'], data['direction'])

            elif data['cmd'] == 'start':
                # Blocks directions that haven't connected
                for direction in self.wait_list:
                    # In those cases where its quicker to connect then i am to add it
                    if direction not in self.direction_connection_dict:
                        self.the_game.blockPathsInDirection(direction)
                if self.wait_list:
                    self.the_game.redrawGameLayout()

                self.the_game.start()
                self._periodic_send_status()

            elif data['cmd'] == 'setup':
                print data['connection_config']
                address_to_direction_dict = defaultdict(list)
                for key, address in data['connection_config'].iteritems():
                    if address != 'BLOCK':
                        address_to_direction_dict[address[0], address[1]].append(key)
                    else:
                        self.the_game.blockPathsInDirection(key)

                for address, direction_list in address_to_direction_dict.iteritems():
                    self._connect_to_direction(address, direction_list)

                self.the_game.redrawGameLayout()
                self.the_game.update_players_migrations()

            elif data['cmd'] == 'close':
                self.send_status_data()
                self._close()

            elif data['cmd'] == 'status':
                self.send_status_data()

            elif data['cmd'] == 'migrate':
                self.the_game.migratePlayer(data)
                self.connection.send(json.dumps({'cmd': 'migrate', 'name': data['name']}))

            elif data['cmd'] == 'flash':
                self.the_game.flash_player(data["name"])

            else:
                print "Strange cmd recived", data

    def _receive_commands_from_master(self):
        while self.running:
            try:
                msg = self.connection.receive(4096)  # Will create problems if not all data is received
                print "Data from master"
                if msg == 0 or msg == '':  # The python program crashed
                    raise socket.error
                self._parse_data(self.connection, msg)
            except socket.error:
                print "Closing connection to Master"
                self._close()
            except Exception as e:
                print "Error:", type(e), e
                traceback.print_exc(file=sys.stdout)
                self._close()

    def send_status_data(self):
        """
        Sends the current score status to the master
        """
        raw_data = {'cmd': 'status', 'score': self.the_game.get_tiles()}
        data = json.dumps(raw_data)
        self.connection.send(data)

    def _close(self):
        self.accept_connections = False
        self.running = False
        print self.connected_clients
        try:
            for client in self.connected_clients:  # closes all the connected clients, just to be sure
                self.server.close(client)
            self.connection.close()
        except Exception as e:  # Don't really care here anymore
            pass

        self.the_game.softQuit()