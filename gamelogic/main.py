from collections import defaultdict
import os
import time
import sys
import random

import pygame
from pygame.locals import *

from gamelogic import gamelayout
import maps.config as gameLayoutConfig

from graphics import Wall, Floor

import settings
from player import Player
from graphics.playergraphics import Player as playerGraphics
from GameConnection import GameConnection
import graphics.powerups

import argparse

RUNNING = 1
PAUSE = 2
END = 3


class WallManMain:
    """The Main WallMan Class"""

    def __init__(self, res=None):
        """Initialize"""
        self.gamelayout = gamelayout.GameLayout()
        self.running = PAUSE
        self.players = dict()
        self.res = res
        pygame.init()
        pygame.mouse.set_visible(False)

    def setup(self, connection):
        fullScreen = 0
        if not self.res:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
            self.res = (pygame.display.list_modes()[0])
            fullScreen = pygame.FULLSCREEN

        self.connection = connection
        self.screen = pygame.display.set_mode(self.res, fullScreen)
        pygame.display.set_caption("WallMan - Alexander Svendsen")

    def drawGameLayout(self, map):
        self.playerSprites = pygame.sprite.Group()
        self.blockSprites = pygame.sprite.Group()
        self.floorSprites = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()

        layout = self.gamelayout.readLayoutAsDict(map)

        self.blockHeight = int(self.res[1] / len(layout))
        self.blockWidth = int(self.res[0] / len(layout[0]))

        x_offset = (self.blockWidth / 2)
        y_offset = (self.blockHeight / 2)

        for y in xrange(len(layout)):
            for x in xrange(len(layout[y])):
                centerPoint = [(x * self.blockWidth) + x_offset, (y * self.blockHeight + y_offset)]
                blockData = layout[y][x]
                if blockData == gameLayoutConfig.FLOOR:
                    self.floorSprites.add(Floor(centerPoint, self.blockWidth, self.blockHeight))
                elif blockData == gameLayoutConfig.BLOCK:
                    self.blockSprites.add(
                        Wall(centerPoint, settings.BLOCKCOLORS, self.blockWidth, self.blockHeight, settings.BLOCKWIDTH))
                elif blockData == gameLayoutConfig.SPEEDUP:
                    self.floorSprites.add(Floor(centerPoint, self.blockWidth, self.blockHeight))
                    self.power_ups.add(graphics.powerups.PowerUp(centerPoint, self.blockWidth, self.blockHeight,
                                                                 "images/speed-icon.png", "SPEED"))
                elif blockData == gameLayoutConfig.LOCK:
                    self.floorSprites.add(Floor(centerPoint, self.blockWidth, self.blockHeight))
                    self.power_ups.add(graphics.powerups.PowerUp(centerPoint, self.blockWidth, self.blockHeight,
                                                                      "images/lock-icon.png", "LOCK"))
                elif blockData == gameLayoutConfig.NUKE:
                    self.floorSprites.add(Floor(centerPoint, self.blockWidth, self.blockHeight))
                    self.power_ups.add(graphics.powerups.PowerUp(centerPoint, self.blockWidth, self.blockHeight,
                                                                 "images/nuke-icon.png", "NUKE"))
                elif blockData == gameLayoutConfig.CLEAN:
                    self.floorSprites.add(Floor(centerPoint, self.blockWidth, self.blockHeight))
                    self.power_ups.add(graphics.powerups.PowerUp(centerPoint, self.blockWidth, self.blockHeight,
                                                                 "images/clean-icon.png", "CLEAN"))

        self.blockSprites.draw(self.screen)
        self.power_ups.draw(self.screen)
        self.layout = layout

    def start(self):
        self.running = RUNNING

    def update_players_migrations(self):
        keys = self.connection.directionConnections.keys()
        connDict = {}
        for key in keys:
            connDict[key] = self.connection.sendPlayerInDirection

        for player in self.players.values():
            player.update_migration(**connDict)

    def newPlayerJoined(self, name):  # TODO: BETTER ERROR SUPPORT

        if name in self.players:
            return "Name taken"

        randomFloor = random.choice(self.floorSprites.sprites())
        while randomFloor.get_marker() != "None":  # TODO change to be better
            randomFloor = random.choice(self.floorSprites.sprites())

        player = Player(playerGraphics(randomFloor.rect.center,  self.blockWidth, self.blockHeight),
                        name)

        randomFloor.mark(player._color, name)

        keys = self.connection.directionConnections.keys()
        connDict = {}
        for key in keys:
            connDict[key] = self.connection.sendPlayerInDirection
        player.update_migration(**connDict)
        player.update_layout(self.layout)
        self.players[name] = player
        self.playerSprites.add(player.sprite_object)
        return "OK"

    #REVIEW: SO MANY HACKS
    def migratePlayer(self, name, direction, newDirection, x, y, color, sprite_x, sprite_y, speed_level):  # FIXME: Should not join to a random place
        if name in self.players:
            return "Name taken"

        x_offset = (self.blockWidth / 2)
        y_offset = (self.blockHeight / 2)
        centerPoint = [(x * self.blockWidth) + x_offset, (y * self.blockHeight + y_offset)]

        player = Player(playerGraphics(centerPoint,
                                       self.blockWidth,
                                       self.blockHeight,
                                       color,
                                       sprite_x,
                                       sprite_y),
                        name,
                        speed_level)

        keys = self.connection.directionConnections.keys()
        connDict = {}
        for key in keys:
            connDict[key] = self.connection.sendPlayerInDirection
        player.update_migration(**connDict)

        if direction == "left":
            player._sprite_object.rect.x = self.res[0] - player.speed
        elif direction == "right":
            player._sprite_object.rect.x = - player._sprite_object.rect.w + player.speed
        elif direction == "up":
            player._sprite_object.rect.y = self.res[1] - player.speed
        elif direction == "down":
            player._sprite_object.rect.y = - player._sprite_object.rect.h + player.speed

        player.update_movement(direction)
        player.update_movement(["none", "left", "right", "up", "down"][newDirection])  # FIXME UGLY AS HELL
        player.update_layout(self.layout)

        self.players[name] = player
        self.playerSprites.add(player.sprite_object)  # fixme: need the old color and askii sprite
        return "OK"

    def movePlayer(self, name, direction):  # TODO: Better error support
        if name in self.players:
            self.players[name].update_movement(direction)
        else:
            print "Error: Non-existing player moved", name  # FIXME means the server is inconsistent

    def get_tiles(self):
        score = defaultdict(lambda: 0)
        for floor in self.floorSprites:
            score[floor.get_marker()] += 1
        return score

    def flash_player(self, name):  # FIXME. should really not go directly to the spriteobject i think
        if name in self.players:
            self.players[name].sprite_object.set_flashing(7)
        else:
            print "Error: Non-existing player moved", name  # FIXME means the server is inconsistent

    def main(self):
        """Main game loop, runs all the code"""
        clock = pygame.time.Clock()

        while self.running == PAUSE:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = END
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = END
            clock.tick(10)  # Don't need many frames as the games is basically paused

            # Enables to draw the players as they join
            self.playerSprites.update()
            self.playerSprites.draw(self.screen)
            pygame.display.flip()

        # THE GAME HAS STARTED
        time.clock()
        while self.running == RUNNING:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = END
                    self.connection.send_status_data()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = END
                        self.connection.send_status_data()

            time_passed = clock.tick(120)
            time_passed_micro_seconds = time_passed / 10.0

            for name in self.players.keys():
                player = self.players[name]
                player.update(time_passed_micro_seconds, self.floorSprites)

                #Time to active awsome powers
                powers = pygame.sprite.spritecollide(player.sprite_object, self.power_ups, True)
                for power in powers:
                    if power.type == "SPEED":
                        player.speed_level += 0.25  #Fixme. should be a method or something
                    elif power.type == "LOCK":
                        for floor in self.floorSprites:
                            floor.lock()
                    elif power.type == "CLEAN":
                        for floor in self.floorSprites:
                            floor.unmark()
                    elif power.type == "NUKE":
                        for floor in self.floorSprites:
                            floor.mark(player._color, player._name)

                if player.delete_me:
                    del self.players[name]
            self.floorSprites.draw(self.screen)
            self.power_ups.draw(self.screen)

            self.playerSprites.update()
            self.playerSprites.draw(self.screen)
            pygame.display.flip()

        self.hardQuit()

    def softQuit(self):
        self.running = END

    def hardQuit(self):
        pygame.quit()
        sys.exit(0)


# May need to demonize the function to support CF
def main():
    if not pygame.font:
        print 'Warning, fonts disabled'
    if not pygame.mixer:
        print 'Warning, sound disabled'

    os.putenv('DISPLAY', ':0')  # Attach to local display. Must have it to work on the display wall

    # Set up arguments
    parser = argparse.ArgumentParser(description="Plays a game of Wallman. Note the external server must be active")
    parser.add_argument("-a", "--address", help="Master address", type=str, default='rocksvv.cs.uit.no')
    parser.add_argument("-p", "--port", help="Master port", type=int, default=65523)
    parser.add_argument("-r", "--res", help="Resolution of the screen", type=int, nargs=2, action='append', default=None)
    parser.add_argument("-m", "--map", help="Which map should be run. Different ones can be fund int hte maps folder",
                        type=str, default='level001.json')
    args = parser.parse_args()

    res = None if not args.res else tuple(args.res[0])

    wallman = WallManMain(res)

    #Connect to master and start reciving commands
    conn = GameConnection(wallman)
    try:
        conn.setup(args.address, args.port)
    except Exception as e:
        print "Can't connect to master"
        print "\t-> Double check the connection point", args.address, args.port
        print e
        sys.exit(0)

    #Setup the main game
    wallman.setup(conn)
    wallman.drawGameLayout(args.map)  # Draw the game layout once, since it should not be updated
    wallman.main()

if __name__ == "__main__":  # TODO REFACTOR THE CODE
    try:
        sys.exit(main())
    except KeyboardInterrupt:  # review  maybe should send status anyway ?
        sys.exit(0)

