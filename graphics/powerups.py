# -*- coding: utf-8 -*-
import pygame


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center_point, width, height, image, type):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (width, height))

        self.rect = self.image.get_rect()

        # Move the rect into the correct position
        self.rect.center = center_point
        self.type = type