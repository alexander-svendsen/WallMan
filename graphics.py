import pygame
from pygame.locals import *
import os

import gamelayout
import maps.config as gameLayoutConfig
from graphics.Block import Block
import settings

BLOCK_SIZE = 24  # TODO MORE DYNAMIC

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
        pygame.display.set_caption("WallMan - Alexander Svendsen")

    def drawGameLayout(self):

        x_offset = (BLOCK_SIZE/2)
        y_offset = (BLOCK_SIZE/2)
        blockSprites = pygame.sprite.Group()
        layout = self.gamelayout.readLayoutAsDict()
        for y in xrange(len(layout)):
            for x in xrange(len(layout[y])):
                centerPoint = [(x * BLOCK_SIZE) + x_offset, (y * BLOCK_SIZE + y_offset)]
                blockData = layout[y][x]
                if blockData == gameLayoutConfig.BLOCK:
                    blockSprites.add(Block(centerPoint, settings.BLOCKCOLORS, BLOCK_SIZE, BLOCK_SIZE, settings.BLOCKWITH))

        blockSprites.draw(self.screen)



    def main(self):
        # Used to manage how fast the screen updates
        """Main game loop, runs all the code"""
        clock = pygame.time.Clock()
        #Draw the game layout once, since it should not be updated
        self.drawGameLayout()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_RIGHT or event.key == K_LEFT or event.key == K_UP or event.key == K_DOWN:
                        pass
            clock.tick(20)
            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    if not pygame.font: print 'Warning, fonts disabled'
    if not pygame.mixer: print 'Warning, sound disabled'
    wallman = WallManMain((500, 570))
    wallman.main()


