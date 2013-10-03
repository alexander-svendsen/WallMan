# -*- coding: utf-8 -*-
import web
import json
import argparse
import thread
import masterconnectionpoint as mcp

urls = (
    '/(.*)', 'Server'
)


class Server:  # Single server controlling all states and players
    def GET(self, path=""):
        if path == "start":
            data = {'cmd': 'start'}
            web.connection_point.send_to_all(json.dumps(data))

    def POST(self, path=""):  # FIXME error messages and such
        if path == "setup":
            web.connection_point.send_setup()

        if path == "join":
            web.connection_point.add_player(web.data())

        if path == "move":
            web.connection_point.move_player(web.data())


if __name__ == "__main__":
    app = web.application(urls, globals())

    # Set up arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Master port", type=int, default=9500)
    parser.add_argument("-sc", "--screen_config",
                        help="Pick a screen config of the available files inside the screenconfig folder",
                        type=str, default="default")
    args = parser.parse_args()

    #Set up the Master connection
    connection_point = mcp.MasterConnectionPoint('0.0.0.0', args.port, args.screen_config, dict())
    web.connection_point = connection_point
    thread.start_new(connection_point.listen_for_slaves, ())

    import sys  # Yuck
    if len(sys.argv) > 1:  # Yuck
        sys.argv[1] = '8080'  # Yuck

    #Start running web.py
    app.run()