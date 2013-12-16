# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import sys
import requests
import time

username = raw_input('Choose a nickname: ')
data = '{"name": "' + username + '"}'
url = 'http://129.242.22.192:8080/'

r = requests.post(url + 'join', data=data)

pygame.init()
screen = pygame.display.set_mode((100, 100))
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            if event.key == K_LEFT:
                start = time.time()

                print "Left"
                data = '{"name": "' + username + '", "direction" : "left"}'
                r = requests.post(url + 'move', data=data)
                end = time.time()
                print end - start
            if event.key == K_RIGHT:
                print "Right"
                data = '{"name": "' + username + '", "direction" : "right"}'
                r = requests.post(url + 'move', data=data)
            if event.key == K_DOWN:
                print "Down"
                data = '{"name": "' + username + '", "direction" : "down"}'
                r = requests.post(url + 'move', data=data)
            if event.key == K_UP:
                print "Up"
                data = '{"name": "' + username + '", "direction" : "up"}'
                r = requests.post(url + 'move', data=data)
            if event.key == K_r:
                data = '{"name": "' + username + '"}'
                r = requests.post(url + 'join', data=data)
            if event.key == SYSWMEVENT:
                print "Delete"
                r = requests.get(url + 'start')
    clock.tick(60)


pygame.quit()
sys.exit()