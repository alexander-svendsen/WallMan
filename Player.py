from pygame.constants import *


class Player():
    def __init__(self):
        self.speed = 3
        self.xMove = 0
        self.yMove = 0

        self.direction = 0
        self.nextDirection = 0

        # To helper directions to decide which path to take
        self.xDirection = [0, -self.speed, self.speed, 0, 0]
        self.yDirection = [0, 0, 0, -self.speed, self.speed]
        self.score = 0 # Unsure if the players themselves should keep score... don't think so

    def updateMovement(self, key):
        self.direction = self.nextDirection  # THINK THIS CREATES ERRORS
        if key == K_LEFT:
            self.nextDirection = 1
        elif key == K_RIGHT:
            self.nextDirection = 2
        elif key == K_UP:
            self.nextDirection = 3
        elif key == K_DOWN:
            self.nextDirection = 4

    def update(self):
        self.xMove = self.xDirection[self.nextDirection]
        self.yMove = self.yDirection[self.nextDirection]
        # TODO: Update view

