# -*- coding: utf-8 -*-
import web
import json
import argparse
import thread
from Master import Master as SlaveServer

urls = (
    '/(.*)', 'Server'
)


class Server:  # Single server controlling all states and players
    def GET(self, path=""):
        if path == "start":
            data = {'cmd': 'start'}
            web.slavesConnectionPoint.sendToAll(json.dumps(data))

    def POST(self, path=""):
        if path == "setup":
            web.slavesConnectionPoint.sendOutSetup()

        if path == "join":
            data = json.loads(web.data())

            if len(web.slavesConnectionPoint) > 0:
                connectionPoint = web.slavesConnectionPoint.getRandomSocket()
                web.players[data["name"]] = connectionPoint
                data["cmd"] = "join"
                connectionPoint.send(json.dumps(data))
            else:
                return "Error No game screens available"

        if path == "move":
            data = json.loads(web.data())

            if data["name"] in web.players:
                data["cmd"] = "move"
                web.players[data["name"]].send(json.dumps(data))
            else:
                return "Not a valid player"


if __name__ == "__main__":
    app = web.application(urls, globals())

    # Set up arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", help="Master address", type=str, default='localhost')
    parser.add_argument("-p", "--port", help="Master port", type=int, default=9500)
    parser.add_argument("-o", "--orientation",
                        help="Pick a orientation of the available files inside the orientation folder",
                        type=str, default="default")
    args = parser.parse_args()

    #Adding a player dict as a shared variable
    web.players = dict()

    #Set up the Master connection
    slavesConnectionPoint = SlaveServer(args.address, args.port, args.orientation, web.players)
    web.slavesConnectionPoint = slavesConnectionPoint
    thread.start_new(slavesConnectionPoint.listen, ())  # TODO: Stop the thread when the game has started

    import sys  # Yuck
    if len(sys.argv) > 1:  # Yuck
        sys.argv[1] = '8080'  # Yuck

    #Start running web.py
    app.run()