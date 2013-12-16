# -*- coding: utf-8 -*-
import pygame


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image, power_type):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (width, height))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = power_type