from pygame.constants import *
import pygame


class Player():
    def __init__(self, spriteRect, playerName, screenRes):
        self.speed = 2  # TODO more dynamic
        self.xMove = 0
        self.yMove = 0

        self.playerName = playerName

        self.oldDirection = 0
        self.direction = 0
        self.spriteRect = spriteRect
        #self.spriteRect = spriteRect

        # To helper directions to decide which path to take
        self.xDirection = [0, -self.speed, self.speed, 0, 0]
        self.yDirection = [0, 0, 0, -self.speed, self.speed]
        self.score = 0  # Unsure if the players themselves should keep score... don't think so
        self.color = spriteRect.color
        self.res = screenRes

    def updateMovement(self, direction):
        if self.oldDirection == 0:  # Only update old direction if the direction has been used
            self.oldDirection = self.direction
        if direction == "left":
            self.direction = 1
        elif direction == "right":
            self.direction = 2
        elif direction == "up":
            self.direction = 3
        elif direction == "down":
            self.direction = 4

    def update(self, spriteBlocks, spriteFloor):
        self.checkIfOfScreen()

        self.xMove = self.xDirection[self.direction]
        self.yMove = self.yDirection[self.direction]

        self.spriteRect.rect.move_ip(self.xMove, self.yMove)

        if pygame.sprite.spritecollideany(self.spriteRect, spriteBlocks):

            self.spriteRect.rect.move_ip(-self.xMove, -self.yMove)

            #If we can't move in the new direction... continue in old direction
            self.xMove = self.xDirection[self.oldDirection]
            self.yMove = self.yDirection[self.oldDirection]
            self.spriteRect.rect.move_ip(self.xMove, self.yMove)

            #If we can't move that direction either, we simply stop
            if pygame.sprite.spritecollideany(self.spriteRect, spriteBlocks):
                self.spriteRect.rect.move_ip(-self.xMove, -self.yMove)
                self.yMove = 0
                self.xMove = 0
                self.oldDirection = 0
                self.direction = 0
        else:  # If we can continue in the new direction, remove the old direction
            self.oldDirection = 0

        # Check if we mark a new floor
        floorCollide = pygame.sprite.spritecollide(self.spriteRect, spriteFloor, False)
        if floorCollide:
            for floor in floorCollide:
                floor.mark(self.color, self.playerName)

    def checkIfOfScreen(self):
        # TODO TELEPORT IN Y AXIS AS WELL
        if self.spriteRect.rect.x >= self.res[0]:
            self.spriteRect.rect.x = - self.spriteRect.rect.w + self.speed
        elif self.spriteRect.rect.x + self.spriteRect.rect.w <= 0:
            self.spriteRect.rect.x = self.res[0] - self.speed


    def getSprite(self):
        return self.spriteRect
