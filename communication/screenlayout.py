# -*- coding: utf-8 -*-
import json
from collections import defaultdict


class ScreenLayout():
    """
    Class to select and use an orientation based on the command line input
    """

    def __init__(self, orientation, path="orientation/"):
        self.__path = path
        self.__idDict = defaultdict(lambda: 0)
        self.default = False
        if orientation == "default":
            self.default = True
            self.__orientation = dict()
            self.__joinList = list()
        else:
            self.__orientation = self.__read(orientation)

    def __read(self, name):
        with open(self.__path + name, 'r') as content_file:
            content = content_file.read()
        return json.loads(content)

    def getIdOfHost(self, hostname):
        """
        Sets up an unique ID for the hostname, to decide how the screens are supposed to be orienteted
        If the default orientation is choosed, an default orientation will be build based on how the screens are added

        :rtype : str basicly hostname_counter
        :param hostname: The hostname to the screen connecting
        """

        if self.__idDict[hostname] == 0:
            uniqueID = hostname
        else:
            uniqueID = hostname + "_{0}".format(str(self.__idDict[hostname]))

        self.__idDict[hostname] += 1

        if self.default:
            if len(self.__joinList) > 0:
                left, right = (self.__joinList[-1], self.__joinList[0])
                self.__orientation[left]["right"] = uniqueID
                self.__orientation[right]["left"] = uniqueID
            else:
                left, right = ('', '')  #TODO Remove the sign
            self.__orientation[uniqueID] = {"left": left, "right": right}
            self.__joinList.append(uniqueID)

        return uniqueID

    def isNameValid(self, name):
        return name in self.__orientation

    def getConnectionSetupForId(self, uniqueID):
        return self.__orientation[uniqueID]



if __name__ == "__main__":
    test1 = ScreenLayout("FailTest.json")
    host = test1.getIdOfHost("Alexander-PC")
    print test1.getConnectionSetupForId(host)

    test2 = ScreenLayout("default")
    host = test2.getIdOfHost("Alexander-PC")
    host = test2.getIdOfHost("Alexander-PC")
    host = test2.getIdOfHost("Alexander-PC")
    print test2.getConnectionSetupForId(host)
