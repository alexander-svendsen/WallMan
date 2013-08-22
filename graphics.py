import os

import pygame
from pygame.locals import *

import gamelayout
import maps.config as gameLayoutConfig
from graphics.wall import Wall
from graphics.player import Player as playerGraphics
import settings
from player import Player
from graphics.floor import Floor
import time

BLOCK_SIZE = 24  # TODO MORE DYNAMIC
playnameList = ["player1", "player2"]

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
        self.players = list()
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
                    player = Player(playerGraphics(centerPoint, BLOCK_SIZE, BLOCK_SIZE), playnameList.pop())
                    self.players.append(player)
                    self.playerSprites.add(player.getSprite())
                    self.floorSprites.add(Floor(centerPoint, BLOCK_SIZE, BLOCK_SIZE))
        self.blockSprites.draw(self.screen)

    def main(self):
        # Used to manage how fast the screen updates
        """Main game loop, runs all the code"""
        clock = pygame.time.Clock()
        #Draw the game layout once, since it should not be updated
        self.drawGameLayout()

        running = True
        time.clock()
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_RIGHT or event.key == K_LEFT or event.key == K_UP or event.key == K_DOWN:
                        self.players[0].updateMovement(event.key)
                    if event.key == K_a or event.key == K_s or event.key == K_d or event.key == K_w:
                        self.players[1].updateMovement(event.key)
            clock.tick(30)

            for player in self.players:
                player.update(self.blockSprites, self.floorSprites)
            self.floorSprites.draw(self.screen)

            self.playerSprites.draw(self.screen)
            pygame.display.flip()
            timer = time.clock()
            if timer > 30:
                print "Game Over ..."
                score = dict()
                for floor in self.floorSprites:
                    try:
                        score[floor.getMarker()] += 1
                    except KeyError:
                        score[floor.getMarker()] = 1
                print score
                running = False
            else:
                print timer

    pygame.quit()


if __name__ == "__main__":
    if not pygame.font: print 'Warning, fonts disabled'
    if not pygame.mixer: print 'Warning, sound disabled'
    wallman = WallManMain((500, 570))
    wallman.main()


