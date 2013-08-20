import pygame


class Wall(pygame.sprite.Sprite):
    def __init__(self, centerPoint, color, width, height, border):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, color, self.rect, border)


        """Move the rect into the correct position"""
        self.rect.center = centerPoint

