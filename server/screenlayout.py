# -*- coding: utf-8 -*-
import copy
import json
import collections


class ScreenLayout():
    """
    Class to select and use an screen connection config. Takes care of figuring out what config is the right one, If the
    host connecting is a valid one and build a default config if such is specified.
    """
    def __init__(self, screen_config_type='default', screen_config_path='screenconfig/'):
        """
        :param screen_config_type: Which type of config should be used. If not specified a default will be used.
        :param screen_config_path: Where can the different kinds of connection configs be found
        """
        self._counter_dict_for_hostname = collections.defaultdict(lambda: 0)
        self._join_list = None
        if screen_config_type == 'default':
            self._join_list = list()
            self._screen_config_dict = dict()
        else:
            self._screen_config_dict = self._read(screen_config_type, screen_config_path)

        self._screen_config_type = screen_config_type

    def _read(self, name, path):
        with open(path + name, 'r') as content_file:
            content = content_file.read()
        return json.loads(content)

    def get_id_of_host(self, hostname):
        """
        Sets up an unique ID for the hostname. Mostly used in case there is suppose to be multiple game screens per host
        If the default screen-config is chosen, an default screen-config will be build based on when the screens joins

        :rtype : the unique hostname
        :param hostname: The hostname to the screen connecting
        """

        #Only doing this to allow writing hostnames without the counter
        if self._counter_dict_for_hostname[hostname]:
            uniqueID = "{0}_{1}".format(hostname, self._counter_dict_for_hostname[hostname])
        else:
            uniqueID = hostname

        self._counter_dict_for_hostname[hostname] += 1

        if self._screen_config_type == 'default':
            self._build_default_orientation(uniqueID)

        return uniqueID

    def _build_default_orientation(self, unique_hostname):
        if self._join_list:
            left, right = (self._join_list[-1], self._join_list[0])
            self._screen_config_dict[left]["right"] = unique_hostname
            self._screen_config_dict[right]["left"] = unique_hostname
            self._screen_config_dict[unique_hostname] = {"left": left, "right": right, "map": "default"}
        else:
            self._screen_config_dict[unique_hostname] = {"map": "default"}
        self._join_list.append(unique_hostname)

    def is_hostname_valid(self, hostname):
        """
        Returns whether or not the hostname is a valid one for this screen config
        :param hostname:
        :return: boolean
        """
        return hostname in self._screen_config_dict

    def _reset_screen_config(self):
        if len(self._join_list) == 1:
            self._screen_config_dict[self._join_list[0]] = {}
            return
        for index, elem in enumerate(self._join_list):
            left, right = (self._join_list[index - 1], self._join_list[(index + 1) % len(self._join_list)])
            self._screen_config_dict[elem]["left"] = left
            self._screen_config_dict[elem]["right"] = right

    def remove(self, hostname):
        """
        Removes the current hostname from the screen config, making it possible for new connections to join.
        Use it when the client disconnects
        :param hostname:
        :return:
        """
        if hostname not in self._screen_config_dict:
            return

        if self._join_list:
            self._join_list.remove(hostname)
            self._reset_screen_config()
            del self._screen_config_dict[hostname]
        else:
            hostname = hostname.rsplit('_', 1)[0]
            self._counter_dict_for_hostname[hostname] -= 1
            print self._counter_dict_for_hostname

    def get_map_for_hostname(self, hostname):
        """
        Returns the map file name for the hostname
        :param hostname:
        :return:
        """
        return self._screen_config_dict[hostname]["map"]

    def __getitem__(self, hostname):
        connection_dict = copy.copy(self._screen_config_dict[hostname])
        del connection_dict["map"]
        return connection_dict

    def __str__(self):
        return '{0}:\n\t{1}'.format(self._screen_config_type, self._screen_config_dict)
