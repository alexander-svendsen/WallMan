import pygame
import random
import string


class Player(pygame.sprite.Sprite):
    def __init__(self, centerPoint, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        pygame.draw.rect(self.image, color, self.rect)

        myfont = pygame.font.SysFont("monospace", (width + height)/2 - 4)
        myfont.set_bold(1)

        #Inverse the colors
        inverseColor = (255 - color[0], 255 - color[1], 255 - color[2])
        label = myfont.render(self.idGenerator(2), 1, inverseColor)
        self.image.blit(label, (0, 0))

        """Move the rect into the correct position"""
        self.rect.center = centerPoint

    def idGenerator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))
