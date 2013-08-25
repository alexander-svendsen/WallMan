# -*- coding: utf-8 -*-
import web
import json

urls = (
    '/(.*)', 'Server'
)


class Server:  #Single server controlling all states and players
    def GET(self):
        return "Hello, world!"

    def POST(self, path=""):
        if path == "join":
            data = json.loads(web.data())
            print data["name"]


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()