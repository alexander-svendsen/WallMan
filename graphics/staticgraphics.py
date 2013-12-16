import pygame
from graphicspriteobject import GraphicSpriteObject

WALL_IMAGE = pygame.image.load("images/brick.png")


class Floor(GraphicSpriteObject):
    def __init__(self, center_point, width, height):
        GraphicSpriteObject.__init__(self, width, height)
        self.drawingRect = pygame.Rect(width / 2 - width / 4, height / 2 - height / 4, width / 2, height / 2)
        self.playerName = "None"
        self.res_size = (width, height)
        self.rect.center = center_point
        self._lock = False

    def mark(self, color, playerName):
        if not self._lock:
            self.image.fill(color, self.drawingRect)
            self.playerName = playerName

    def unmark(self):
        self.image.fill((0, 0, 0), self.drawingRect)
        self.playerName = "None"

    def get_marker(self):
        return self.playerName

    def lock(self):
        self._lock = True


class Wall(pygame.sprite.Sprite):
    def __init__(self, center_point, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = WALL_IMAGE
        self.image = pygame.transform.scale(self.image, (width, height))

        self.rect = self.image.get_rect()
        self.rect.center = center_point



