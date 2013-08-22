import pygame


class Floor(pygame.sprite.Sprite):
    def __init__(self, centerPoint, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.set_alpha(128)
        self.rect = self.image.get_rect()

        # Move the rect into the correct position
        self.rect.center = centerPoint
        self.drawingRect = pygame.Rect(width / 2 - width / 4, height / 2 - height / 4, width / 2, height / 2)
        self.playerName = "None"

    def mark(self, color, playerName):
        self.image.fill(color, self.drawingRect)
        self.playerName = playerName

    def getMarker(self):
        return self.playerName

    def unmark(self):
        pass

