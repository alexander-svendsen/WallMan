import pygame
from pygame.locals import *


class WallManMain:
    """The Main WallMan Class"""
    
    def __init__(self, width=640,height=480):
        """Initialize"""
        """Initialize PyGame"""
        pygame.init()
        self.width = width
    	self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))

    def main(self):
    	"""Main game loop, runs all the code"""

    	running = True
    	while running:
			for event in pygame.event.get():
				if event.type == QUIT:
					running = False
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						running = False

    pygame.quit()

if __name__ == "__main__":
	if not pygame.font: print 'Warning, fonts disabled'
	if not pygame.mixer: print 'Warning, sound disabled'
	wallman = WallManMain()
	wallman.main()


