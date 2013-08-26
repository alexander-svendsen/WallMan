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

BLOCK_SIZE = 24  # TODO MORE DYNAMIC
playnameList = ["player1", "player2"]

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

        self.width, self.height = res
        self.screen = pygame.display.set_mode(res, fullScreen)
        self.players = dict()
        pygame.display.set_caption("WallMan - Alexander Svendsen")

    def drawGameLayout(self):

        x_offset = (BLOCK_SIZE / 2)
        y_offset = (BLOCK_SIZE / 2)

        self.playerSprites = pygame.sprite.Group()
        self.blockSprites = pygame.sprite.Group()
        self.floorSprites = pygame.sprite.Group()

        layout = self.gamelayout.readLayoutAsDict()
        for y in xrange(len(layout)):
            for x in xrange(len(layout[y])):
                centerPoint = [(x * BLOCK_SIZE) + x_offset, (y * BLOCK_SIZE + y_offset)]
                blockData = layout[y][x]
                if blockData == gameLayoutConfig.FLOOR:
                    self.floorSprites.add(Floor(centerPoint, BLOCK_SIZE, BLOCK_SIZE))
                if blockData == gameLayoutConfig.BLOCK:
                    self.blockSprites.add(
                        Wall(centerPoint, settings.BLOCKCOLORS, BLOCK_SIZE, BLOCK_SIZE, settings.BLOCKWITH))
                if blockData == gameLayoutConfig.PLAYER:
                    # TODO AUTO ADD PLAYERS INSTEAD OF THIS
                    #player = Player(playerGraphics(centerPoint, BLOCK_SIZE, BLOCK_SIZE), playnameList.pop())
                    #self.players.append(player)
                    #self.playerSprites.add(player.getSprite())
                    self.floorSprites.add(Floor(centerPoint, BLOCK_SIZE, BLOCK_SIZE))
        self.blockSprites.draw(self.screen)

    def start(self):
        self.running = RUNNING

    def newPlayerJoined(self, name):  # TODO: BETTER ERROR SUPPORT

        if name in self.players:
            return "Name taken"

        randomFloor = random.choice(self.floorSprites.sprites())
        while randomFloor.getMarker() != "None":  # TODO change to be better
            randomFloor = random.choice(self.floorSprites.sprites())

        player = Player(playerGraphics(randomFloor.rect.center, BLOCK_SIZE, BLOCK_SIZE), name)
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
        self.running = PAUSE
        while self.running == PAUSE:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = END
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = END
            clock.tick(30)
            pygame.display.flip()

            # Enables to draw the players as they join
            self.playerSprites.draw(self.screen)

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
                print player
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
                print timer

        pygame.quit()
        sys.exit()



if __name__ == "__main__":
    if not pygame.font: print 'Warning, fonts disabled'
    if not pygame.mixer: print 'Warning, sound disabled'
    wallman = WallManMain((500, 570))
    wallman.drawGameLayout()  # Draw the game layout once, since it should not be updated
    #To start web server
    app = web.application(urls, globals())
    web.game = wallman
    thread.start_new_thread(app.run, ())
    wallman.main()


