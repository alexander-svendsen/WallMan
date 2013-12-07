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

import tools
from player import Player
from graphics.playergraphics import Player as playerGraphics
from gameconnection import *
import graphics.powerups

import argparse

RUNNING = 1
PAUSE = 2
END = 3
MEASUREMENT = tools.Measure()


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
        self.map = None
        self.floorRight = list()
        self.floorLeft = list()
        self.floorUp = list()
        self.floorDown = list()
        self.time_passed_micro_seconds = 0.0

    def setup(self, connection):
        fullScreen = 0
        if not self.res:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
            self.res = (pygame.display.list_modes()[0])
            fullScreen = pygame.FULLSCREEN

        self.connection = connection
        self.screen = pygame.display.set_mode(self.res, fullScreen)
        pygame.display.set_caption("WallMan - Alexander Svendsen")

    def checkCorners(self, x, y, max_x, max_y, floor):
        if y == 0:
            self.floorUp.append((x, y, floor))
        if y == max_y:
            self.floorDown.append((x, y, floor))
        if x == 0:
            self.floorLeft.append((x, y, floor))
        if x == max_x:
            self.floorRight.append((x, y, floor))

    def change_floor_to_wall(self, floors):
        for floor_info in floors:
            self.floorSprites.remove(floor_info[2])
            self.blockSprites.add(
                Wall(floor_info[2].rect.center,
                     tools.BLOCKCOLORS,
                     floor_info[2].res_size[0],
                     floor_info[2].res_size[0],
                     tools.BLOCKWIDTH))
            self.layout[floor_info[1]][floor_info[0]] = gameLayoutConfig.BLOCK
        return []

    def blockPathsInDirection(self, direction):
        if direction == "right":
            self.floorRight = self.change_floor_to_wall(self.floorRight)
        elif direction == "left":
            self.floorLeft = self.change_floor_to_wall(self.floorLeft)
        elif direction == "down":
            self.floorUp = self.change_floor_to_wall(self.floorUp)
        elif direction == "up":
            self.floorDown = self.change_floor_to_wall(self.floorDown)

    def redrawGameLayout(self):
        for player in self.players.values():
            player.update_layout(self.layout)

        self.blockSprites.draw(self.screen)

    def drawGameLayout(self):
        if self.map is None:
            print "Error: Map not set"
            self.hardQuit()
            return

        self.playerSprites = pygame.sprite.Group()
        self.blockSprites = pygame.sprite.Group()
        self.floorSprites = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()

        layout = self.gamelayout.readLayoutAsDict(self.map)

        self.blockHeight = int(self.res[1] / len(layout))
        self.blockWidth = int(self.res[0] / len(layout[0]))

        rest_height = self.res[1] - (self.blockHeight * len(layout))
        rest_width = self.res[0] - (self.blockWidth * len(layout[0]))

        x_offset = (self.blockWidth / 2)
        y_offset = (self.blockHeight / 2)
        blockHeight = self.blockHeight
        blockWidth = self.blockWidth
        print blockHeight, blockWidth
        print "w", rest_height
        print "h", rest_width

        for y in xrange(len(layout)):
            for x in xrange(len(layout[y])):
                if y == len(layout) - 1:
                    blockHeight = self.blockHeight + rest_height
                    y_off = blockHeight / 2
                else:
                    blockHeight = self.blockHeight
                    y_off = y_offset

                if x == len(layout[y]) - 1:
                    blockWidth = self.blockWidth + rest_width
                    x_off = blockWidth / 2
                else:
                    blockWidth = self.blockWidth
                    x_off = x_offset

                centerPoint = [(x * self.blockWidth) + x_off, (y * self.blockHeight + y_off)]
                blockData = layout[y][x]
                if blockData == gameLayoutConfig.FLOOR:
                    floor = Floor(centerPoint, blockWidth, blockHeight)
                    self.floorSprites.add(floor)
                    self.checkCorners(x, y, len(layout[y]) - 1, len(layout) - 1, floor) #fixme a must for all tests
                elif blockData == gameLayoutConfig.BLOCK:
                    self.blockSprites.add(
                        Wall(centerPoint, blockWidth, blockHeight))
                elif blockData == gameLayoutConfig.SPEEDUP:  # FIXME can refactor all of these to the same thing
                    self.floorSprites.add(Floor(centerPoint, blockWidth, blockHeight))
                    self.power_ups.add(graphics.powerups.PowerUp(centerPoint, blockWidth, blockHeight,
                                                                 "images/speed-icon.png", "SPEED"))
                elif blockData == gameLayoutConfig.LOCK:
                    self.floorSprites.add(Floor(centerPoint, blockWidth, blockHeight))
                    self.power_ups.add(graphics.powerups.PowerUp(centerPoint, blockWidth, blockHeight,
                                                                      "images/lock-icon.png", "LOCK"))
                elif blockData == gameLayoutConfig.NUKE:
                    self.floorSprites.add(Floor(centerPoint, blockWidth, blockHeight))
                    self.power_ups.add(graphics.powerups.PowerUp(centerPoint, blockWidth, blockHeight,
                                                                 "images/nuke-icon.png", "NUKE"))
                elif blockData == gameLayoutConfig.CLEAN:
                    self.floorSprites.add(Floor(centerPoint, blockWidth, blockHeight))
                    self.power_ups.add(graphics.powerups.PowerUp(centerPoint, blockWidth, blockHeight,
                                                                 "images/clean-icon.png", "CLEAN"))

        self.blockSprites.draw(self.screen)
        self.power_ups.draw(self.screen)
        self.layout = layout

    def start(self):
        self.running = RUNNING
        MEASUREMENT.make_note("Game started")

    def update_players_migrations(self):
        keys = self.connection.direction_connection_dict.keys()
        connDict = {}
        for key in keys:
            connDict[key] = self.connection.send_player_in_direction

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

        keys = self.connection.direction_connection_dict.keys()
        connDict = {}
        for key in keys:
            connDict[key] = self.connection.send_player_in_direction
        player.update_migration(**connDict)
        player.update_layout(self.layout)
        self.players[name] = player
        self.playerSprites.add(player.sprite_object)

        MEASUREMENT.make_note("New player migrated in: " + str(len(self.players)))
        return "OK"

    #REVIEW: SO MANY HACKS
    def migratePlayer(self, data):
        if data['name'] in self.players:
            return "Name taken"

        x_offset = (self.blockWidth / 2)
        y_offset = (self.blockHeight / 2)
        centerPoint = [(data['x'] * self.blockWidth) + x_offset, (data['y'] * self.blockHeight + y_offset)]

        player = Player(playerGraphics(centerPoint,
                                       self.blockWidth,
                                       self.blockHeight,
                                       data['color'],
                                       data['sprite_x'],
                                       data['sprite_y']),
                        data['name'])

        player.speed_level = data['speed_level']

        keys = self.connection.direction_connection_dict.keys()
        connDict = {}
        for key in keys:
            connDict[key] = self.connection.send_player_in_direction
        player.update_migration(**connDict)

        #Setts where the player will come in at
        #Fixme may be a wrong speed to use
        if data['direction'] == "left":
            player._sprite_object.rect.x = self.res[0] - data['speed_level'] * self.time_passed_micro_seconds
        elif data['direction'] == "right":
            player._sprite_object.rect.x = - player._sprite_object.rect.w + data['speed_level'] * self.time_passed_micro_seconds
        elif data['direction'] == "up":
            player._sprite_object.rect.y = self.res[1] - data['speed_level'] * self.time_passed_micro_seconds
        elif data['direction'] == "down":
            player._sprite_object.rect.y = - player._sprite_object.rect.h + data['speed_level'] * self.time_passed_micro_seconds

        player.update_movement(data['direction'])
        player.update_movement(["none", "left", "right", "up", "down"][data['newDirection']])  # FIXME UGLY AS HELL
        player.update_layout(self.layout)

        self.players[data['name']] = player
        self.playerSprites.add(player.sprite_object)

        MEASUREMENT.make_note("New player joined: " + str(len(self.players)))

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

            time_passed = clock.tick(60)
            self.time_passed_micro_seconds = time_passed / 10.0

            for name in self.players.keys():
                player = self.players[name]
                player.update(self.time_passed_micro_seconds, self.floorSprites)

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
                    self.playerSprites.remove(self.players[name].sprite_object)
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
    parser.add_argument("-m", "--measure", help="Should game resources be measured", type=bool, default=False)
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

    if args.measure:
        thread.start_new(MEASUREMENT.start_measurement, (1, ))
        MEASUREMENT.write_to_file = True

    #Setup the main game
    wallman.setup(conn)
    wallman.drawGameLayout()  # Draw the game layout once, since it should not be updated
    wallman.main()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:  # review  maybe should send status anyway ?
        sys.exit(0)

