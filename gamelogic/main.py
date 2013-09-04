import os
import time
import sys
import random
import thread

import pygame
from pygame.locals import *

from gamelogic import gamelayout
import maps.config as gameLayoutConfig

from graphics.wall import Wall
from graphics.floor import Floor

import settings
from player import Player
from graphics.player import Player as playerGraphics

from communication.server import *

RUNNING = 1
PAUSE = 2
END = 3


class WallManMain:
    """The Main WallMan Class"""

    def __init__(self, res=None):
        """Initialize"""
        self.gamelayout = gamelayout.GameLayout()

        pygame.init()
        fullScreen = 0
        if res is None:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
            res = (pygame.display.list_modes()[0])
            fullScreen = pygame.FULLSCREEN

        self.screen = pygame.display.set_mode(res, fullScreen)
        self.players = dict()
        self.res = res
        pygame.display.set_caption("WallMan - Alexander Svendsen")

    def drawGameLayout(self):


        self.playerSprites = pygame.sprite.Group()
        self.blockSprites = pygame.sprite.Group()
        self.floorSprites = pygame.sprite.Group()

        layout = self.gamelayout.readLayoutAsDict()

        print self.res
        print "Height of the course:", len(layout)
        print "Width of the course:", len(layout[0])
        self.blockHeight = int(self.res[1] / len(layout))
        self.blockWidth = int(self.res[0] / len(layout[0]))
        print "Block height:", self.blockHeight
        print "Block width:", self.blockWidth


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

        self.blockSprites.draw(self.screen)
        self.layout = layout

    def start(self):
        self.running = RUNNING

    def newPlayerJoined(self, name):  # TODO: BETTER ERROR SUPPORT

        if name in self.players:
            return "Name taken"

        randomFloor = random.choice(self.floorSprites.sprites())
        while randomFloor.getMarker() != "None":  # TODO change to be better
            randomFloor = random.choice(self.floorSprites.sprites())

        print randomFloor.rect.center, self.blockWidth, self.blockHeight
        player = Player(playerGraphics(randomFloor.rect.center,  self.blockWidth, self.blockHeight), name, self.layout, self.res)
        print player.getSprite().rect
        randomFloor.mark(player.color, name)

        self.players[name] = player
        self.playerSprites.add(player.getSprite())
        return "OK"

    def movePlayer(self, name, direction):  # TODO: Better error support
        self.players[name].updateMovement(direction)

    def main(self):
        # Used to manage how fast the screen updates
        """Main game loop, runs all the code"""
        clock = pygame.time.Clock()

        # PAUSE
        self.running = PAUSE
        while self.running == PAUSE:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = END
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = END
            clock.tick(10)  # Don't need many frames as the games is basically paused

            # Enables to draw the players as they join
            self.playerSprites.draw(self.screen)
            pygame.display.flip()

        # THE GAME HAS STARTED
        time.clock()
        while self.running == RUNNING:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = END
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = END

            clock.tick(30)

            for player in self.players.values():
                player.update(self.blockSprites, self.floorSprites)
            self.floorSprites.draw(self.screen)

            self.playerSprites.draw(self.screen)
            pygame.display.flip()

            timer = time.clock()
            if timer > 60:  # TODO make more dynamic
                print "Game Over ..."
                score = dict()
                for floor in self.floorSprites:
                    try:
                        score[floor.getMarker()] += 1
                    except KeyError:
                        score[floor.getMarker()] = 1
                print score
                self.running = END
            else:
                pass
                #print timer

        pygame.quit()
        sys.exit()



if __name__ == "__main__":
    if not pygame.font: print 'Warning, fonts disabled'
    if not pygame.mixer: print 'Warning, sound disabled'
    wallman = WallManMain((528, 528))
    wallman.drawGameLayout()  # Draw the game layout once, since it should not be updated
    #To start web server
    app = web.application(urls, globals())
    web.game = wallman
    thread.start_new_thread(app.run, ())
    wallman.main()


