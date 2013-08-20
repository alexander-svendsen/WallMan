from pygame.constants import *
import pygame


class Player():
    def __init__(self, spriteRect):
        self.speed = 3
        self.xMove = 0
        self.yMove = 0

        self.direction = 0
        self.nextDirection = 0
        self.spriteRect = spriteRect
        #self.spriteRect = spriteRect

        # To helper directions to decide which path to take
        self.xDirection = [0, -self.speed, self.speed, 0, 0]
        self.yDirection = [0, 0, 0, -self.speed, self.speed]
        self.score = 0  # Unsure if the players themselves should keep score... don't think so

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

    def update(self, spriteBlocks, spriteFloor):  # TODO REMOVE STOP BUG
        self.xMove = self.xDirection[self.nextDirection]
        self.yMove = self.yDirection[self.nextDirection]

        self.spriteRect.rect.move_ip(self.xMove, self.yMove)

        if pygame.sprite.spritecollide(self.spriteRect, spriteBlocks, False):
            self.spriteRect.rect.move_ip(-self.xMove, -self.yMove)

            #IF we can't move in the new direction... continue in old direction
            self.xMove = self.xDirection[self.direction]
            self.yMove = self.yDirection[self.direction]
            self.spriteRect.rect.move_ip(self.xMove, self.yMove)

            if pygame.sprite.spritecollide(self.spriteRect, spriteBlocks, False):
                self.spriteRect.rect.move_ip(-self.xMove, -self.yMove)
                self.yMove = 0
                self.xMove = 0
                self.direction = 0
                self.nextDirection = 0
        else:
            self.direction = 0

        floorColide = pygame.sprite.spritecollide(self.spriteRect, spriteFloor, False)
        if floorColide:
            for floor in floorColide:
                floor.mark()




    def getSprite(self):
        return self.spriteRect
