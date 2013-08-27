# -*- coding: utf-8 -*-
import web
import json


#Steps:
# Make the game run
    # Problem the threads get killed after executing stuff. Where to start it then?
# Make the game wait until the server tells it to start
# Make it possible for a player to join the game
# Make it possible to control the palyer
# When the game is over the server should shut down
    # Problem the thread dosn't stop even tough it should. Pygame dosn't shut down....

urls = (
    '/(.*)', 'Server'
)


class Server:  # Single server controlling all states and players
    def GET(self, path=""):
        if path == "start":
            web.game.start()

    def POST(self, path=""):
        if path == "join":  # Don't really like this approch but seems like this is the only way webpy wants it
            print web.data()
            data = json.loads(web.data())
            return web.game.newPlayerJoined(data["name"])
        if path == "move":
            data = json.loads(web.data())
            web.game.movePlayer(data["name"], data["direction"])


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
