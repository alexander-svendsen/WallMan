import pygame
import random
import string
from graphicspriteobject import GraphicSpriteObject
import time

class Player(GraphicSpriteObject):
    def __init__(self, centerPoint, width, height, color=None, askii=None, inverse_color=None):
        GraphicSpriteObject.__init__(self, width, height)
        self.color = self._generate_color(color)
        self.image.fill(self.color, self.rect)
        #pygame.draw.rect(self.image, self.color, self.rect)
        self.drawingRect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h)

        #Inverse the colors and set the random askii in the player
        self.inverse_color = self._generate_inverse_color(inverse_color, self.color)
        self.id = self._generator_random_askii(askii, 2)
        myfont = pygame.font.SysFont("monospace", (width + height) / 2 - 4)
        myfont.set_bold(1)
        self.label = myfont.render(self.id, 1, self.inverse_color)
        self.image.blit(self.label, (0, 0))

        # Move the rect into the correct position
        self.rect.center = centerPoint
        self.times_flashing = 0

    def set_flashing(self, times_flashing):
        self.times_flashing = times_flashing
        self._flash = True
        self.start_time = -0.25

    def update(self):
        #print "WOOOOT", self.display
        if self.times_flashing:
            if (time.clock() - self.start_time) >= 0.25:
                self._flash = not self._flash
                self.start_time = time.clock()
                self.times_flashing -= 1
                if self._flash and self.times_flashing:
                    self.image.fill((0, 0, 0), self.drawingRect)
                else:
                    self.image.fill(self.color, self.drawingRect)
                    self.image.blit(self.label, (0, 0))




    @staticmethod
    def _generator_random_askii(askii, size=6, chars=string.ascii_uppercase + string.digits):
        if askii:
            return askii
        return ''.join(random.choice(chars) for _ in range(size))

    @staticmethod
    def _generate_color(color):
        if color:
            return color
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    @staticmethod
    def _generate_inverse_color(inverse_color, color):
        if inverse_color:
            return inverse_color
        return  255 - color[0], 255 - color[1], 255 - color[2]