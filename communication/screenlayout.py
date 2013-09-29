# -*- coding: utf-8 -*-
import json
from collections import defaultdict


class ScreenLayout():
    """
    Class to select and use an screen connection config based on the command line input
    """

    def __init__(self, screen_config_type='default', screen_config_path='orientation/'):
        """
        :param screen_config_type: Which type of config should be used. If not specified a default will be used.
        :param screen_config_path: Where can the different kinds of connection configs be found
        """
        self._idDict = defaultdict(lambda: 0)

        if screen_config_type == 'default':
            self._screen_config_dict = dict()
            self._joinList = list()
        else:
            self._screen_config_dict = self._read(screen_config_type, screen_config_path)

        self._screen_config_type = screen_config_type

    def _read(self, name, path):
        with open(path + name, 'r') as content_file:
            content = content_file.read()
        return json.loads(content)

    def get_id_of_host(self, hostname):
        """
        Sets up an unique ID for the hostname. Mostly used in case there is suppose to be multiple game screen per host
        If the default orientation is chosen, an default orientation will be build based on when the screens joins

        :rtype : the unique hostname
        :param hostname: The hostname to the screen connecting
        """

        #Only doing this to allow writing hostnames without the counter
        if self._idDict[hostname]:
            uniqueID = "{0}_{1}".format(hostname, self._idDict[hostname])
        else:
            uniqueID = hostname

        self._idDict[hostname] += 1

        if self._screen_config_type == 'default':
            self._build_default_orientation(uniqueID)

        return uniqueID

    def _build_default_orientation(self, unique_hostname):
        if self._joinList:
            left, right = (self._joinList[-1], self._joinList[0])
            self._screen_config_dict[left]["right"] = unique_hostname
            self._screen_config_dict[right]["left"] = unique_hostname
            self._screen_config_dict[unique_hostname] = {"left": left, "right": right}
        else:
            self._screen_config_dict[unique_hostname] = {}
        self._joinList.append(unique_hostname)

    def is_hostname_valid(self, name):
        return name in self._screen_config_dict

    def get_connection_setup_for_hostname(self, uniqueID):
        return self._screen_config_dict[uniqueID]

    def __str__(self):
        return '{0}:\n\t{1}'.format(self._screen_config_type, self._screen_config_dict)


if __name__ == "__main__":
    test1 = ScreenLayout("FailTest.json")
    host = test1.get_id_of_host("Alexander-PC")
    if test1.is_hostname_valid(host):
        print test1.get_connection_setup_for_hostname(host)
    else:
        print "Host unvalid: {}".format(host)

    def printTest(host, screenLayout):
        print '{0}:\n\t{1}'.format(host, screenLayout.get_connection_setup_for_hostname(host))

    test2 = ScreenLayout("SingleScreenTest.json")
    printTest(test2.get_id_of_host("Alexander-PC"), test2)
    printTest(test2.get_id_of_host("Alexander-PC"), test2)
    printTest(test2.get_id_of_host("Alexander-PC"), test2)
    printTest(test2.get_id_of_host("Alexander-PC"), test2)

    test3 = ScreenLayout('default')
    host = test3.get_id_of_host("Alexander-PC")
    print test3
    print "left" in test3.get_connection_setup_for_hostname(host)

    test3.get_id_of_host("Alexander-PC")
    print test3
