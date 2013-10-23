import pygame
import random
import string
from graphicspriteobject import GraphicSpriteObject
import time


class Player(GraphicSpriteObject):
    def __init__(self, centerPoint, width, height, color=None, sprite_x=None, sprite_y=None):
        GraphicSpriteObject.__init__(self, width, height)
        self.color = self._generate_color(color)

        self.drawingRect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h)

        self.drawImage = pygame.Surface([width, height])
        self.drawImage.fill(self.color, self.rect)

        self.x = sprite_x if sprite_x else random.randint(0, 24)
        self.y = sprite_y if sprite_y else random.randint(0, 19)
        pokemon_image = pygame.image.load("images/pokemon.png")  # review a more efficent way for this ?
        pos = pygame.Rect(self.x * 80, self.y * 80, 80, 80)
        pokeImage = pokemon_image.subsurface(pos)
        pokeImage = pygame.transform.scale(pokeImage, (width, height))

        self.drawImage.blit(pokeImage, (0, 0))

        self.image.blit(self.drawImage, (0, 0))

        # Move the rect into the correct position
        self.rect.center = centerPoint
        self.times_flashing = 0

    def set_flashing(self, times_flashing):
        self.times_flashing = times_flashing
        self._flash = True
        self.start_time = -0.25

    def update(self):
        if self.times_flashing:
            if (time.clock() - self.start_time) >= 0.25:
                self._flash = not self._flash
                self.start_time = time.clock()
                self.times_flashing -= 1
                if self._flash and self.times_flashing:
                    self.image.fill((0, 0, 0), self.drawingRect)
                else:
                    self.image.blit(self.drawImage, (0, 0))

    @staticmethod
    def _generate_color(color):
        if color:
            return color
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
