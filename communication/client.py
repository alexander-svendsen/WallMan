# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import sys
import urllib2
import urllib

nb = raw_input('Choose a nickname: ')
url = 'http://129.242.22.192:8080/join'
req = urllib2.Request(url)
req.add_data('{"name" : "%s"}' % nb)
print urllib2.urlopen(req)

pygame.init()
screen = pygame.display.set_mode((50, 50))
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
                print "Left"
                url = 'http://129.242.22.192:8080/move'
                req = urllib2.Request(url)
                req.add_data('{"name" : "%s", "direction" : "left"}' % nb)
                urllib2.urlopen(req)
            if event.key == K_RIGHT:
                print "Right"
                url = 'http://129.242.22.192:8080/move'
                req = urllib2.Request(url)
                req.add_data('{"name" : "%s", "direction" : "right"}' % nb)
                urllib2.urlopen(req)
            if event.key == K_DOWN:
                print "Down"
                url = 'http://129.242.22.192:8080/move'
                req = urllib2.Request(url)
                req.add_data('{"name" : "%s", "direction" : "down"}' % nb)
                urllib2.urlopen(req)
            if event.key == K_UP:
                print "Up"
                url = 'http://129.242.22.192:8080/move'
                req = urllib2.Request(url)
                req.add_data('{"name" : "%s", "direction" : "up"}' % nb)
                urllib2.urlopen(req)

            if event.key == K_r:
                url = 'http://129.242.22.192:8080/join'
                req = urllib2.Request(url)
                req.add_data('{"name" : "%s"}' % nb)
                urllib2.urlopen(req)
            if event.key == SYSWMEVENT:
                print "Delete"
                url = 'http://129.242.22.192:8080/start'
                req = urllib2.Request(url)
                urllib2.urlopen(req)


pygame.quit()
sys.exit()