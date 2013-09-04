import pygame
import maps.config as gameLayoutConfig


NONE = 0
LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4


class Player():
    def __init__(self, spriteRect, playerName, layout, res):
        self.speed = 3  # TODO more dynamic
        self.xMove = 0
        self.yMove = 0
        self.res = res

        self.playerName = playerName

        self.currentDirection = 0
        self.newDirection = 0
        self.spriteRect = spriteRect

        # To helper directions to decide which path to take
        self.xDirection = [0, -self.speed, self.speed, 0, 0]  # TODO: REFACTOR THIS
        self.yDirection = [0, 0, 0, -self.speed, self.speed]
        self.color = spriteRect.color

        # TODO: DO I NEED THEM ?
        self.layout = layout
        self.layoutWidth = len(layout)
        self.layoutHeight = len(layout[0])

    def updateMovement(self, direction):
        #if self.oldDirection == 0:  # Only update old direction if the direction has been used
        #    self.oldDirection = self.direction
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
        x = self.spriteRect.rect.center[0] / self.spriteRect.rect.w
        y = self.spriteRect.rect.center[1] / self.spriteRect.rect.h
        if direction == LEFT:
            length = self.lengthToNextBlock(x, self.spriteRect.rect.w, self.spriteRect.rect.x)
            if length <= 0:
                return length
        elif direction == RIGHT:
            length = self.lengthToNextBlock(x, self.spriteRect.rect.w, self.spriteRect.rect.x)
            if length >= 0:
                return length
        elif direction == UP:
            length = self.lengthToNextBlock(y, self.spriteRect.rect.h, self.spriteRect.rect.y)
            if length <= 0:
                return length
        elif direction == DOWN:
            length = self.lengthToNextBlock(y, self.spriteRect.rect.h, self.spriteRect.rect.y)
            if length >= 0:
                return length
        return self.speed  #TODO: REFACTOR

    def move(self, direction, speed):
        x = self.spriteRect.rect.center[0] / self.spriteRect.rect.w
        y = self.spriteRect.rect.center[1] / self.spriteRect.rect.h
        self.yMove = self.yDirection[direction]
        self.xMove = self.xDirection[direction]

        if direction == LEFT:
            if self.isWall(y, x - 1):
                length = self.lengthToNextBlock(x, self.spriteRect.rect.w, self.spriteRect.rect.x)
                if abs(length) >= speed:
                    self.xMove = self.xDirection[LEFT]
                else:
                    self.xMove = length

        elif direction == RIGHT:
            if self.isWall(y, x + 1):
                length = self.lengthToNextBlock(x, self.spriteRect.rect.w, self.spriteRect.rect.x)
                if abs(length) >= speed:
                    self.xMove = self.xDirection[RIGHT]
                else:
                    self.xMove = length

        elif direction == UP:
            if self.isWall(y - 1, x):
                length = self.lengthToNextBlock(y, self.spriteRect.rect.h, self.spriteRect.rect.y)
                if abs(length) >= speed:
                    self.yMove = self.yDirection[UP]
                else:
                    self.yMove = length

        elif direction == DOWN:
            if self.isWall(y + 1, x):
                length = self.lengthToNextBlock(y, self.spriteRect.rect.h, self.spriteRect.rect.y)
                if abs(length) >= speed:
                    self.yMove = self.yDirection[DOWN]
                else:
                    self.yMove = length

    def directionHasAwall(self, direction):
        x = self.spriteRect.rect.center[0] / self.spriteRect.rect.w
        y = self.spriteRect.rect.center[1] / self.spriteRect.rect.h
        if direction == LEFT:
            return self.isWall(y, x - 1)
        elif direction == RIGHT:
            return self.isWall(y, x + 1)
        elif direction == UP:
            return self.isWall(y - 1, x)
        elif direction == DOWN:
            return self.isWall(y + 1, x)

    def getSpeed(self, speed, direction):
        return [0, -speed, speed,0,0][direction],[0,0,0,-speed,speed][direction]

    def update(self, spriteBlocks, spriteFloor):
        #self.checkIfOfScreen()

        # Algorithm
        # If new direction
            # delta = length to next block, next block is decided from current direction
            # if delta < speed & block in new direction is not a wall
                # move player delta - speed
                # move player new direction
                # current direction = new direction
                #new direction = 0
            # else:
                # move speed... don't think i need this
        # else
            # move current direction

        if self.newDirection != NONE:
            delta = self.calculateLengthToNextBlockBasedOnDirection(self.currentDirection)
            if abs(delta) < self.speed:
                self.xMove, self.yMove = self.getSpeed(abs(delta), self.currentDirection)
                if self.directionHasAwall(self.newDirection):
                    restspeed = self.getSpeed(self.speed - abs(delta), self.currentDirection)
                    self.move(self.currentDirection, restspeed)
                else:
                    self.currentDirection = self.newDirection
                    self.newDirection = NONE
        else:
            self.move(self.currentDirection, self.speed)

        self.spriteRect.rect.move_ip(self.xMove, self.yMove)

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
