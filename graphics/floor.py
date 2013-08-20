import pygame


class Floor(pygame.sprite.Sprite):
    def __init__(self, centerPoint, width, height, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.set_alpha(128)
        self.rect = self.image.get_rect()
        self.color = color

        """Move the rect into the correct position"""
        self.rect.center = centerPoint

    def mark(self):  # TODO , better update of the Floor
        self.image.fill((255,255,255))

    def unmark(self):
        pass

