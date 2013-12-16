import json


# Could add a lot of functions as map editors and such come into place
class MapTools():
    def __init__(self, path="game/maps/"):
        self.path = path

    def read_map_as_dict(self, name="default"):
        if name == "default":
            name = "level001.json"
        with open(self.path + name, 'r') as content_file:
            content = content_file.read()
        return json.loads(content)




