from collections import defaultdict
import os
import time
import sys
import random

import pygame
from pygame.locals import *

from gamelogic import gamelayout
import maps.config as GameLayoutConfig

from graphics import Wall, Floor

import tools
from player import Player
from graphics.playergraphics import Player as player_graphics
from gameconnection import *
import graphics.powerups

import argparse

RUNNING = 1
PAUSE = 2
END = 3
MEASUREMENT = tools.Measure()


class WallManMain:
    """The Main WallMan Class. Responsible for everything that has anything to do with the game logic"""

    def __init__(self, res=None):
        self.game_layout = gamelayout.GameLayout()
        self.running = PAUSE
        self.players = dict()
        self.res = res
        pygame.init()
        pygame.mouse.set_visible(False)
        self.map = None
        self.floor_right = list()
        self.floor_left = list()
        self.floor_up = list()
        self.floor_down = list()
        self.time_passed_micro_seconds = 0.0

        self.player_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group()
        self.floor_sprites = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()

    def setup(self, connection):
        full_screen = 0
        if not self.res:
            #So the pygame window starts at the upper left corner
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
            self.res = (pygame.display.list_modes()[0])
            full_screen = pygame.FULLSCREEN

        self.connection = connection
        self.screen = pygame.display.set_mode(self.res, full_screen)
        pygame.display.set_caption("WallMan")

    def _check_corners(self, x, y, max_x, max_y, floor):
        if y == 0:
            self.floor_up.append((x, y, floor))
        if y == max_y:
            self.floor_down.append((x, y, floor))
        if x == 0:
            self.floor_left.append((x, y, floor))
        if x == max_x:
            self.floor_right.append((x, y, floor))

    def _change_floor_to_wall(self, floors):
        for floor_info in floors:
            self.floor_sprites.remove(floor_info[2])
            self.block_sprites.add(
                Wall(floor_info[2].rect.center,
                     floor_info[2].res_size[0],
                     floor_info[2].res_size[0]))
            self.layout[floor_info[1]][floor_info[0]] = GameLayoutConfig.WALL
        return []

    def block_paths_in_direction(self, direction):
        if direction == "right":
            self.floor_right = self._change_floor_to_wall(self.floor_right)
        elif direction == "left":
            self.floor_left = self._change_floor_to_wall(self.floor_left)
        elif direction == "down":
            self.floor_up = self._change_floor_to_wall(self.floor_up)
        elif direction == "up":
            self.floor_down = self._change_floor_to_wall(self.floor_down)

    def redraw_game_layout(self):
        for player in self.players.values():
            player.update_layout(self.layout)

        self.block_sprites.draw(self.screen)

    def draw_game_layout(self):
        if self.map is None:
            print "Error: Map not set"
            self.hard_quit()
            return

        self.layout = self.game_layout.read_layout_as_dict(self.map)

        self.block_height = int(self.res[1] / len(self.layout))
        self.block_width = int(self.res[0] / len(self.layout[0]))

        rest_height = self.res[1] - (self.block_height * len(self.layout))
        rest_width = self.res[0] - (self.block_width * len(self.layout[0]))

        x_offset = (self.block_width / 2)
        y_offset = (self.block_height / 2)
        tmp_block_height = self.block_height
        tmp_block_width = self.block_width

        for y in xrange(len(self.layout)):
            for x in xrange(len(self.layout[y])):
                if y == len(self.layout) - 1:
                    tmp_block_height = self.block_height + rest_height
                    y_off = tmp_block_height / 2
                else:
                    tmp_block_height = self.block_height
                    y_off = y_offset

                if x == len(self.layout[y]) - 1:
                    tmp_block_width = self.block_width + rest_width
                    x_off = tmp_block_width / 2
                else:
                    tmp_block_width = self.block_width
                    x_off = x_offset

                center_point = [(x * self.block_width) + x_off, (y * self.block_height + y_off)]
                block_data = self.layout[y][x]
                if block_data == GameLayoutConfig.FLOOR:
                    floor = Floor(center_point, tmp_block_width, tmp_block_height)
                    self.floor_sprites.add(floor)
                    self._check_corners(x, y, len(self.layout[y]) - 1, len(self.layout) - 1, floor)
                elif block_data == GameLayoutConfig.WALL:
                    self.block_sprites.add(Wall(center_point, tmp_block_width, tmp_block_height))
                elif block_data == GameLayoutConfig.SPEEDUP:
                    self.floor_sprites.add(Floor(center_point, tmp_block_width, tmp_block_height))
                    self.power_ups.add(graphics.powerups.PowerUp(center_point, tmp_block_width, tmp_block_height,
                                                                 "images/speed-icon.png", "SPEED"))
                    self._check_corners(x, y, len(self.layout[y]) - 1, len(self.layout) - 1, floor)
                elif block_data == GameLayoutConfig.LOCK:
                    self.floor_sprites.add(Floor(center_point, tmp_block_width, tmp_block_height))
                    self.power_ups.add(graphics.powerups.PowerUp(center_point, tmp_block_width, tmp_block_height,
                                                                      "images/lock-icon.png", "LOCK"))
                    self._check_corners(x, y, len(self.layout[y]) - 1, len(self.layout) - 1, floor)
                elif block_data == GameLayoutConfig.NUKE:
                    self.floor_sprites.add(Floor(center_point, tmp_block_width, tmp_block_height))
                    self.power_ups.add(graphics.powerups.PowerUp(center_point, tmp_block_width, tmp_block_height,
                                                                 "images/nuke-icon.png", "NUKE"))
                    self._check_corners(x, y, len(self.layout[y]) - 1, len(self.layout) - 1, floor)
                elif block_data == GameLayoutConfig.TRASH:
                    self.floor_sprites.add(Floor(center_point, tmp_block_width, tmp_block_height))
                    self.power_ups.add(graphics.powerups.PowerUp(center_point, tmp_block_width, tmp_block_height,
                                                                 "images/clean-icon.png", "TRASH"))
                    self._check_corners(x, y, len(self.layout[y]) - 1, len(self.layout) - 1, floor)

        self.block_sprites.draw(self.screen)
        self.power_ups.draw(self.screen)

    def start(self):
        self.running = RUNNING
        MEASUREMENT.make_note("Game started")

    def update_players_migrations(self):
        keys = self.connection.direction_connection_dict.keys()
        connDict = {}
        for key in keys:
            connDict[key] = self.connection.send_player_in_direction

        for player in self.players.values():
            player.update_migration(**connDict)

    def new_player_joined(self, name):

        if name in self.players:
            return "Name taken"

        random_floor = random.choice(self.floor_sprites.sprites())
        while random_floor.get_marker() != "None":
            random_floor = random.choice(self.floor_sprites.sprites())

        player = Player(player_graphics(random_floor.rect.center,  self.block_width, self.block_height), name)
        random_floor.mark(player._color, name)

        keys = self.connection.direction_connection_dict.keys()
        connDict = {}
        for key in keys:
            connDict[key] = self.connection.send_player_in_direction
        player.update_migration(**connDict)
        player.update_layout(self.layout)
        self.players[name] = player
        self.player_sprites.add(player.sprite_object)

        MEASUREMENT.make_note("New player migrated in: " + str(len(self.players)))
        return "OK"

    def migratePlayer(self, data):
        if data['name'] in self.players:
            return "Name taken"

        x_offset = (self.block_width / 2)
        y_offset = (self.block_height / 2)
        centerPoint = [(data['x'] * self.block_width) + x_offset, (data['y'] * self.block_height + y_offset)]

        player = Player(player_graphics(centerPoint,
                                       self.block_width,
                                       self.block_height,
                                       data['color'],
                                       data['sprite_x'],
                                       data['sprite_y']),
                        data['name'])

        player.speed_level = data['speed_level']

        keys = self.connection.direction_connection_dict.keys()
        connDict = {}
        for key in keys:
            connDict[key] = self.connection.send_player_in_direction
        player.update_migration(**connDict)

        #Setts where the player will come in at
        if data['direction'] == "left":
            player._sprite_object.rect.x = self.res[0] - data['speed_level'] * self.time_passed_micro_seconds
        elif data['direction'] == "right":
            player._sprite_object.rect.x = - player._sprite_object.rect.w + data['speed_level'] * self.time_passed_micro_seconds
        elif data['direction'] == "up":
            player._sprite_object.rect.y = self.res[1] - data['speed_level'] * self.time_passed_micro_seconds
        elif data['direction'] == "down":
            player._sprite_object.rect.y = - player._sprite_object.rect.h + data['speed_level'] * self.time_passed_micro_seconds

        player.update_movement(data['direction'])
        player.update_movement(["none", "left", "right", "up", "down"][data['newDirection']])
        player.update_layout(self.layout)

        self.players[data['name']] = player
        self.player_sprites.add(player.sprite_object)

        MEASUREMENT.make_note("New player joined: " + str(len(self.players)))

        return "OK"

    def move_player(self, name, direction):
        if name in self.players:
            self.players[name].update_movement(direction)
        else:
            print "Error: Non-existing player moved", name

    def get_tiles(self):
        score = defaultdict(lambda: 0)
        for floor in self.floor_sprites:
            score[floor.get_marker()] += 1
        return score

    def flash_player(self, name):
        if name in self.players:
            self.players[name].sprite_object.set_flashing(7)
        else:
            print "Error: Non-existing player moved", name

    def main(self):

        clock = pygame.time.Clock()

        while self.running == PAUSE:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = END
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = END
            clock.tick(10)  # Don't need many frames as the games is basically paused

            # Enables to draw the players as they join
            self.player_sprites.update()
            self.player_sprites.draw(self.screen)
            pygame.display.flip()

        # THE GAME HAS STARTED
        time.clock()
        while self.running == RUNNING:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = END
                    self.connection.send_status_data()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = END
                        self.connection.send_status_data()

            time_passed = clock.tick(60)
            self.time_passed_micro_seconds = time_passed / 10.0

            for name in self.players.keys():
                player = self.players[name]
                player.update(self.time_passed_micro_seconds, self.floor_sprites)

                #Time to active awesome powers
                powers = pygame.sprite.spritecollide(player.sprite_object, self.power_ups, True)
                for power in powers:
                    if power.type == "SPEED":
                        player.increase_player_speed(0.25)
                    elif power.type == "LOCK":
                        for floor in self.floor_sprites:
                            floor.lock()
                    elif power.type == "TRASH":
                        for floor in self.floor_sprites:
                            floor.unmark()
                    elif power.type == "NUKE":
                        for floor in self.floor_sprites:
                            floor.mark(player._color, player._name)

                if player.delete_me:
                    self.player_sprites.remove(self.players[name].sprite_object)
                    del self.players[name]
            self.floor_sprites.draw(self.screen)
            self.power_ups.draw(self.screen)

            self.player_sprites.update()
            self.player_sprites.draw(self.screen)
            pygame.display.flip()

        self.hard_quit()

    def soft_quit(self):
        self.running = END

    def hard_quit(self):
        pygame.quit()
        sys.exit(0)


def main():
    if not pygame.font:
        print 'Warning, fonts disabled'
    if not pygame.mixer:
        print 'Warning, sound disabled'

    os.putenv('DISPLAY', ':0')  # Attach to local display. Must have it to work on the display wall

    # Set up arguments
    parser = argparse.ArgumentParser(description="Plays a game of Wallman. Note the external server must be active")
    parser.add_argument("-a", "--address", help="Master address", type=str, default='rocksvv.cs.uit.no')
    parser.add_argument("-p", "--port", help="Master port", type=int, default=65523)
    parser.add_argument("-r", "--res", help="Resolution of the screen", type=int, nargs=2, action='append', default=None)
    parser.add_argument("-m", "--measure", help="Should game resources be measured", type=bool, default=False)
    args = parser.parse_args()

    res = None if not args.res else tuple(args.res[0])

    wallman = WallManMain(res)

    #Connect to master and start receiving commands
    conn = GameConnection(wallman)
    try:
        conn.setup(args.address, args.port)
    except Exception as e:
        print "Can't connect to master"
        print "\t-> Double check the connection point", args.address, args.port
        print e
        sys.exit(0)

    if args.measure:
        thread.start_new(MEASUREMENT.start_measurement, (1, ))
        MEASUREMENT.write_to_file = True

    #Setup the main game
    wallman.setup(conn)
    wallman.draw_game_layout()  # Draw the game layout once, since it should not be updated
    wallman.main()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)

