import json


class GameLayout():
    def __init__(self, path="maps/"):
        self.path = path

    def read_layout_as_dict(self, name="default"):
        if name == "default":
            name = "level001.json"
        with open(self.path + name, 'r') as content_file:
            content = content_file.read()
        return json.loads(content)




