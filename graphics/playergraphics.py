import pygame
import random
import string
from graphicspriteobject import GraphicSpriteObject
import time

POKEMON_IMAGE = pygame.image.load("images/pokemon.png")


class Player(GraphicSpriteObject):
    def __init__(self, centerPoint, width, height, color=None, sprite_x=None, sprite_y=None):
        GraphicSpriteObject.__init__(self, width, height)
        self.color = self._generate_color(color)

        self.drawingRect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h)

        self.drawImage = pygame.Surface([width, height])
        self.drawImage.fill(self.color, self.rect)

        #since the last row of pokemon's isn't filled totally out, we ignore them
        self.x = sprite_x if sprite_x else random.randint(0, 23)
        self.y = sprite_y if sprite_y else random.randint(0, 18)
        pokemon_image = POKEMON_IMAGE
        pos = pygame.Rect(self.x * 80, self.y * 80, 80, 80)
        pokeImage = pokemon_image.subsurface(pos)
        pokeImage = pygame.transform.scale(pokeImage, (width, height))

        self.drawImage.blit(pokeImage, (0, 0))

        self.image.blit(self.drawImage, (0, 0))

        self.rect.center = centerPoint
        self.times_flashing = 0

    def set_flashing(self, times_flashing):
        self.times_flashing = times_flashing
        self._flash = True
        self.start_time = -0.25

    def update(self):
        if self.times_flashing:
            if (time.time() - self.start_time) >= 0.25:
                self._flash = not self._flash
                self.start_time = time.time()
                self.times_flashing -= 1
                if self._flash and self.times_flashing:
                    self.image.fill((0, 0, 0), self.drawingRect)
                else:
                    self.image.blit(self.drawImage, (0, 0))

    @staticmethod
    def _generate_color(color):
        if color:
            return color
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        while color[0] + color[1] + color[2] < 125:  # TO guarantee not the darkest colors is shown
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return color