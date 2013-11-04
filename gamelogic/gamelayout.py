import json


class GameLayout():
    def __init__(self, path="maps/"):
        self.path = path

    def readLayoutAsDict(self, name="default"):
        if name == "default":
            name = "level001.json"
        with open(self.path + name, 'r') as content_file:
            content = content_file.read()
        return json.loads(content)

    def savelayout(self, name, levelData):
        #TODO:  Auto Generate name ? Throw exception when no levelData
        """Function for level editing, in the future"""
        f = open(name, 'w')
        f.write(levelData)

    def getRandomLayout(self):  # TODO
        raise "NOT IMPLEMENTED YET"


