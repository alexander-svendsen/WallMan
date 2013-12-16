# -*- coding: utf-8 -*-
import json
import argparse
import thread
import sys
import signal
import masterconnectionpoint as mcp
import flask

app = flask.Flask(__name__)


@app.route("/")
def start():
    return flask.redirect(flask.url_for('static', filename='start.html'))


@app.route("/start", methods=['GET'])
def start_game():
    app.connection_point.start_game()
    return status(200)


@app.route("/status", methods=['GET'])
def get_status():
    return json.dumps(app.connection_point.get_status())


@app.route("/setup", methods=['GET'])
def set_setup():
    app.connection_point.send_setup()
    return status(200)


@app.route("/join", methods=['POST'])
def join_game():
    app.connection_point.add_player(flask.request.data)
    return status(200)


@app.route("/move", methods=['POST'])
def move_player():
    app.connection_point.move_player(flask.request.data)
    return status(200)


@app.route("/close", methods=['GET'])
def close_games():
    app.connection_point.shutdown_clients()
    return status(200)


@app.route("/doubletap", methods=['POST'])
def double_tap():
    app.connection_point.flash_player(flask.request.data)
    return status(200)


def status(status):
    response = flask.make_response()
    response.status_code = status
    response.data = response.status
    return response


def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    sys.exit(0)


def main():
    # Set up arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-ps", "--port_server", help="Server for http client port", type=int, default=35001)
    parser.add_argument("-pm", "--port_master", help="Master port toward the game instances", type=int, default=65523)
    parser.add_argument("-sc", "--screen_config",
                        help="Pick a screen config of the available files inside the screenconfig folder",
                        type=str, default="default")
    parser.add_argument("-t", "--time", help="How long should the game run before it shutdown, in second", type=int)
    parser.add_argument("-m", "--measure", help="Should game resources be measured", type=bool, default=False)
    args = parser.parse_args()

    #Set up the Master connection
    connection_point = mcp.MasterConnectionPoint('0.0.0.0',
                                                 args.port_master,
                                                 args.screen_config,
                                                 args.time,
                                                 args.measure)

    app.connection_point = connection_point
    thread.start_new(connection_point.listen_for_slaves, ())

    signal.signal(signal.SIGINT, signal_handler)
    #Start running flask
    app.run(host='0.0.0.0', port=args.port_server)

if __name__ == "__main__":
    sys.exit(main())
