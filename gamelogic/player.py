import pygame
import maps.config as gameLayoutConfig


NONE = 0
LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4


class Player():
    def __init__(self, spriteRect, playerName, layout, res):
        self.speed = 7  # TODO more dynamic
        assert self.speed <= spriteRect.rect.w, "Speed can never be greater then the width of the player"
        assert self.speed <= spriteRect.rect.h, "Speed can never be greater then the height of the player"

        self.xMove = 0
        self.yMove = 0
        self.res = res

        self.playerName = playerName

        self.currentDirection = 0
        self.newDirection = 0
        self.spriteRect = spriteRect
        self.color = spriteRect.color

        #The position in the layout. Set in the update method
        self.x = 0
        self.y = 0

        # To helper directions to decide which path to take
        self.xDirection = [0, -self.speed, self.speed, 0, 0]
        self.yDirection = [0, 0, 0, -self.speed, self.speed]

        self.layout = layout

    def updateMovement(self, direction):
        if direction == "left":
            self.newDirection = LEFT
        elif direction == "right":
            self.newDirection = RIGHT
        elif direction == "up":
            self.newDirection = UP
        elif direction == "down":
            self.newDirection = DOWN

        if self.currentDirection == NONE:
            self.currentDirection = self.newDirection
            self.newDirection = NONE

    def isWall(self, y, x):
        return self.layout[y][x] == gameLayoutConfig.BLOCK

    def lengthToNextBlock(self, blockPos, playerSize, playerCoordinate):
        return blockPos * playerSize - playerCoordinate

    def getNextBlock(self, x, y, direction):
        return [0, (y, x - 1), (y, x + 1), (y - 1, x), (y + 1, x)][direction]

    def calculateLengthToNextBlockBasedOnDirection(self, direction):
        if direction == LEFT:
            length = self.lengthToNextBlock(self.x, self.spriteRect.rect.w, self.spriteRect.rect.x)
            if length <= 0:
                return length
        elif direction == RIGHT:
            length = self.lengthToNextBlock(self.x, self.spriteRect.rect.w, self.spriteRect.rect.x)
            if length >= 0:
                return length
        elif direction == UP:
            length = self.lengthToNextBlock(self.y, self.spriteRect.rect.h, self.spriteRect.rect.y)
            if length <= 0:
                return length
        elif direction == DOWN:
            length = self.lengthToNextBlock(self.y, self.spriteRect.rect.h, self.spriteRect.rect.y)
            if length >= 0:
                return length
        return self.speed

    def move(self, direction, speed):
        self.xMove, self.yMove = self.getSpeed(self.speed, direction)
        if self.isThereAWallInDirection(direction):
            length = self.calculateLengthToNextBlockBasedOnDirection(direction)
            if abs(length) >= speed:
                self.xMove, self.yMove = self.getSpeed(speed, direction)
            else:
                self.xMove, self.yMove = self.getSpeed(abs(length), direction)

    def isThereAWallInDirection(self, direction):
        if direction == LEFT:
            return self.isWall(self.y, self.x - 1)
        elif direction == RIGHT:
            return self.isWall(self.y, self.x + 1)
        elif direction == UP:
            return self.isWall(self.y - 1, self.x)
        elif direction == DOWN:
            return self.isWall(self.y + 1, self.x)

    def getSpeed(self, speed, direction):
        return [0, -speed, speed, 0, 0][direction], [0, 0, 0, -speed, speed][direction]

    def calculateCurrentPositionInLayout(self):
        self.x = self.spriteRect.rect.center[0] / self.spriteRect.rect.w
        self.y = self.spriteRect.rect.center[1] / self.spriteRect.rect.h

    def update(self, spriteFloor):
        #self.checkIfOfScreen()

        self.calculateCurrentPositionInLayout()
        if self.newDirection != NONE:
            delta = self.calculateLengthToNextBlockBasedOnDirection(self.currentDirection)
            if abs(delta) < self.speed:
                if self.isThereAWallInDirection(self.newDirection):
                    restSpeed = self.getSpeed(self.speed - abs(delta), self.currentDirection)
                    self.move(self.currentDirection, restSpeed)
                else:
                    self.xMove, self.yMove = self.getSpeed(abs(delta), self.currentDirection)
                    self.currentDirection = self.newDirection
                    self.newDirection = NONE
        else:
            self.move(self.currentDirection, self.speed)

        self.spriteRect.rect.move_ip(self.xMove, self.yMove)

        # TODO refactor out collision
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
