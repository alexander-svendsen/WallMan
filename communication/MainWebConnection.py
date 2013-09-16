# -*- coding: utf-8 -*-
import web
import json
import argparse
import thread
from SocketCommunication import Server as SlaveServer

urls = (
    '/(.*)', 'Server'
)


class Server:  # Single server controlling all states and players
    def GET(self, path=""):
        if path == "start":
            data = {'cmd': 'start'}
            web.slavesConnectionPoint.send(json.dumps(data))

    def POST(self, path=""):
        if path == "join":  # Don't really like this approch but seems like this is the only way webpy wants it
            print web.data()
            data = json.loads(web.data())
            data["cmd"] = "join"
            web.slavesConnectionPoint.send(json.dumps(data))
        if path == "move":
            data = json.loads(web.data())
            data["cmd"] = "move"
            web.slavesConnectionPoint.send(json.dumps(data))



if __name__ == "__main__":
    app = web.application(urls, globals())

    # Set up arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", help="Master address", type=str, default='localhost')
    parser.add_argument("-p", "--port", help="Master port", type=int, default=9500)
    args = parser.parse_args()

    #Set up a slave pool
    slavesConnectionPoint = SlaveServer(args.address, args.port)
    web.slavesConnectionPoint = slavesConnectionPoint
    thread.start_new(slavesConnectionPoint.connect, ())  # TODO: Stop the thread when the game has started

    app.run()
