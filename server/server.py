# -*- coding: utf-8 -*-
import json
import argparse
import thread
import sys
import web
import masterconnectionpoint as mcp

urls = (
    '/(.*)', 'Server'
)


class Server:
    """
    The main server. It should have the master server stored as a parameter. This class itself only handle the REST
    requests and forward them to the master server. All the REST request are all handled by a separate thread by the
    help of web.py
    """
    def GET(self, path=""):
        if path == "start":
            web.connection_point.start_game()
        if path == "status":
            return json.dumps(web.connection_point.get_status())

    def POST(self, path=""):  # FIXME error messages and such
        if path == "setup":
            web.connection_point.send_setup()

        if path == "join":
            web.connection_point.add_player(web.data())

        if path == "move":
            web.connection_point.move_player(web.data())

        if path == "close":
            web.connection_point.shutdown_clients()

        if path == "doubletap":
            web.connection_point.flash_player(web.data())


def main():
    app = web.application(urls, globals())

    # Set up arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-ps", "--port_server", help="Server for http client port", type=str, default='35001')
    parser.add_argument("-pm", "--port_master", help="Master port", type=int, default=65523)
    parser.add_argument("-sc", "--screen_config",
                        help="Pick a screen config of the available files inside the screenconfig folder",
                        type=str, default="default")
    parser.add_argument("-t", "--time", help="How long should the game run before it shutdown, in second", type=int)
    args = parser.parse_args()

    #Set up the Master connection
    connection_point = mcp.MasterConnectionPoint('0.0.0.0', args.port_master, args.screen_config, args.time)
    web.connection_point = connection_point
    thread.start_new(connection_point.listen_for_slaves, ())

    #web.py ones its own set of special input parameters, so need to give it the parameters it wants and remove the
    #current ones
    import sys  # Yuck
    sys.argv.append("bleh")  # Yuck
    sys.argv[1] = args.port_server  # Yuck

    #Start running web.py
    app.run()

if __name__ == "__main__":
    sys.exit(main())
