# -*- coding: utf-8 -*-
import json
from communication.SocketCommunication import *


class GameConnection():
    def __init__(self):
        pass

    def connectToMaster(self, addr, port):
        self.master = Slave()
        self.master.connect(addr, port)

    def start(self, theGame):
        while True:
            try:
                msg = self.master.receive(1024)
                data = json.loads(msg)
                print data
                if data['cmd'] == "join":
                    print "new player joining"
                    theGame.newPlayerJoined(data["name"])
                elif data['cmd'] == "move":
                    theGame.movePlayer(data["name"], data["direction"])
                elif data['cmd'] == "start":
                    theGame.start()

            except Exception as e:
                print "Closing connection to Master"
                print e




if __name__ == "__main__":
    # if len(sys.argv) == 2:
    #     print "Start server test"
    #     server = Server('0.0.0.0', 30689)
    #     thread.start_new_thread(server.connect, (None, ))
    #     time.sleep(5)
    #     print "start reciving"
    #     try:
    #         print server.recive(1000)
    #     except Exception as e:
    #         print e
    #         print server.recive(1000)
    #     print "closing the shit"
    #     server.recive(1000)
    #
    # else:
    #     client = Client()
    #     client.connect('localhost',30689)
    #     time.sleep(10)
    #     client.connect('localhost',30689)
    #     client.send("mordi")
    #
    #     client.close()

    pass