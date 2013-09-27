import pygame
import random
import string


class Player(pygame.sprite.Sprite):
    def __init__(self, centerPoint, width, height, color=None, id=None, inversedColor=None):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()

        if color is None:
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            self.color = color
        pygame.draw.rect(self.image, self.color, self.rect)

        myfont = pygame.font.SysFont("monospace", (width + height)/2 - 4)
        myfont.set_bold(1)

        #Inverse the colors
        if inversedColor is None:
            self.inverseColor = (255 - self.color[0], 255 - self.color[1], 255 - self.color[2])
        else:
            self.inverseColor = inversedColor

        if id is None:
            self.id = self.idGenerator(2)
        else:
            self.id = id

        label = myfont.render(self.id, 1, self.inverseColor)
        self.image.blit(label, (0, 0))

        """Move the rect into the correct position"""
        self.rect.center = centerPoint

    def idGenerator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))
