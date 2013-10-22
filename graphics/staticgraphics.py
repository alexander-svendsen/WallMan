import pygame
from graphicspriteobject import GraphicSpriteObject


class Floor(GraphicSpriteObject):
    def __init__(self, center_point, width, height):
        GraphicSpriteObject.__init__(self, width, height)
        self.drawingRect = pygame.Rect(width / 2 - width / 4, height / 2 - height / 4, width / 2, height / 2)
        self.playerName = "None"

        # Move the rect into the correct position
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


class Wall(GraphicSpriteObject):
    def __init__(self, center_point, color, width, height, border):
        GraphicSpriteObject.__init__(self, width, height)
        pygame.draw.rect(self.image, color, self.rect, border)

        # Move the rect into the correct position
        self.rect.center = center_point



