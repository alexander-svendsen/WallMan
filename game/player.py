from collections import namedtuple
import pygame
import maps.config as map_config

NONE = 0
LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4

STATE_MOVE_FREELY = 0
STATE_MOVE_RIGHT_OUT_OF_SCREEN = 1
STATE_MOVE_LEFT_OUT_OF_SCREEN = 2
STATE_MOVE_UP_OUT_OF_SCREEN = 3
STATE_MOVE_DOWN_OUT_OF_SCREEN = 4

#Dict to convert which way we actually are moving from string to int
MOVEMENT_CONVERTER_DICT = {"none": NONE, "left": LEFT, "right": RIGHT, "up": UP, "down": DOWN}


class Player():
    def __init__(self, sprite_object, name, speed=1.5):
        self.speed = 0.0
        self.speed_level = (sprite_object.rect.w + sprite_object.rect.h) * speed / 40
        assert self.speed_level <= sprite_object.rect.w, "Speed can never be greater then the width of the player"
        assert self.speed_level <= sprite_object.rect.h, "Speed can never be greater then the height of the player"

        self._migrate_me_in_the_same_game = True
        self._migrate_me_to_another_screen = False
        self.delete_me = False

        self._x_move = 0  # movement in x direction
        self._y_move = 0  # movement in y direction

        self._name = name

        self._current_direction = NONE
        self._new_direction = NONE

        self._sprite_object = sprite_object
        self._color = sprite_object.color

        #Dict to run the decide which function to use base on the state
        self._state_dict = {STATE_MOVE_FREELY: self._move_freely,
                            STATE_MOVE_DOWN_OUT_OF_SCREEN: self._move_down_of_screen,
                            STATE_MOVE_LEFT_OUT_OF_SCREEN: self._move_left_of_screen,
                            STATE_MOVE_RIGHT_OUT_OF_SCREEN: self._move_right_of_screen,
                            STATE_MOVE_UP_OUT_OF_SCREEN: self._move_up_of_screen}

        self._x = 0  # The x position in the map. calculated later
        self._y = 0  # The y position in the map. calculated later

        self._state = STATE_MOVE_FREELY

    def increase_player_speed(self, speed):
        self.speed_level += speed
        if self.speed_level >= self.sprite_object.rect.w:
            self.speed_level = self.sprite_object.rect.w - 1
        if self.speed_level >= self.sprite_object.rect.h:
            self.speed_level = self.sprite_object.rect.h -1

    def update_migration(self, **kwargs):
        self.migrate = {LEFT:   self._migrate if "left" not in kwargs else kwargs["left"],
                        RIGHT:  self._migrate if "right" not in kwargs else kwargs["right"],
                        UP:     self._migrate if "up" not in kwargs else kwargs["up"],
                        DOWN:   self._migrate if "down" not in kwargs else kwargs["down"]}

    def update_map(self, map_array):
        self.map_array = map_array
        self.map_height = len(map_array)
        self.map_width = len(map_array[0])
        Resolution = namedtuple('Resolution', ['width', 'height'])
        self._res = Resolution(self.map_width * self._sprite_object.rect.w,
                               self.map_height * self.sprite_object.rect.h)

    def update_movement(self, direction):
        self._new_direction = MOVEMENT_CONVERTER_DICT[direction]
        if self._current_direction == NONE:
            self._current_direction = self._new_direction
            self._new_direction = NONE

    def _is_wall(self, y, x):
        if x >= self.map_width or x < 0:
            return False
        if 0 > y or y >= self.map_height:
            return False
        return self.map_array[y][x] == map_config.WALL

    def _length_to_next_block(self, blockPos, playerSize, playerCoordinate):
        return blockPos * playerSize - playerCoordinate

    def _length_to_next_block_based_on_direction(self, direction):
        if direction == LEFT:
            length = self._length_to_next_block(self._x, self._sprite_object.rect.w, self._sprite_object.rect.x)
            if length <= 0:
                return length
        elif direction == RIGHT:
            length = self._length_to_next_block(self._x, self._sprite_object.rect.w, self._sprite_object.rect.x)
            if length >= 0:
                return length
        elif direction == UP:
            length = self._length_to_next_block(self._y, self._sprite_object.rect.h, self._sprite_object.rect.y)
            if length <= 0:
                return length
        elif direction == DOWN:
            length = self._length_to_next_block(self._y, self._sprite_object.rect.h, self._sprite_object.rect.y)
            if length >= 0:
                return length
        return self.speed

    def _next_block(self, x, y, direction):
        return [0, (y, x - 1), (y, x + 1), (y - 1, x), (y + 1, x)][direction]

    def _is_there_wall_in_direction(self, direction):
        next_block = self._next_block(self._x, self._y, direction)
        return self._is_wall(*next_block)

    def _get_speed(self, speed, direction):
        return [0, -speed, speed, 0, 0][direction], [0, 0, 0, -speed, speed][direction]

    def _move(self, direction):
        self._x_move, self._y_move = self._get_speed(self.speed, direction)
        if self._is_there_wall_in_direction(direction):
            length = self._length_to_next_block_based_on_direction(direction)
            if abs(length) >= self.speed:
                self._x_move, self._y_move = self._get_speed(self.speed, direction)
            else:
                self._x_move, self._y_move = self._get_speed(abs(length), direction)

    def _calculate_current_position_in_map(self):
        self._x = self._sprite_object.rect.center[0] / self._sprite_object.rect.w
        self._y = self._sprite_object.rect.center[1] / self._sprite_object.rect.h

    def update(self, time, floor_sprites):
        self.speed = self.speed_level * time
        self._calculate_current_position_in_map()

        # Don't need to update the state if we are to move out of the screen
        if self._state == STATE_MOVE_FREELY:
            self._update_state_of_player()

        self._state_dict[self._state]()

        self._check_floor_collision(floor_sprites)
        self._sprite_object.rect.move_ip(self._x_move, self._y_move)

    def _check_floor_collision(self, sprite_floor):
        floorCollide = pygame.sprite.spritecollide(self._sprite_object, sprite_floor, False)
        if floorCollide:
            for floor in floorCollide:
                floor.mark(self._color, self._name)

    def _update_state_of_player(self):
        if self._sprite_object.rect.x + self._sprite_object.rect.w > self._res.width and self._current_direction == RIGHT:
            if self.migrate[RIGHT] != self._migrate:
                self._migrate_me_to_another_screen = True
                self._migrate_me_in_the_same_game = False
            self._state = STATE_MOVE_RIGHT_OUT_OF_SCREEN
        elif self._sprite_object.rect.x < 0 and self._current_direction == LEFT:
            if self.migrate[LEFT] != self._migrate:
                self._migrate_me_to_another_screen = True
                self._migrate_me_in_the_same_game = False
            self._state = STATE_MOVE_LEFT_OUT_OF_SCREEN
        elif self._sprite_object.rect.y + self._sprite_object.rect.h > self._res.height and self._current_direction == DOWN:
            if self.migrate[DOWN] != self._migrate:
                self._migrate_me_to_another_screen = True
                self._migrate_me_in_the_same_game = False
            self._state = STATE_MOVE_DOWN_OUT_OF_SCREEN
        elif self._sprite_object.rect.y < 0 and self._current_direction == UP:
            if self.migrate[UP] != self._migrate:
                self._migrate_me_to_another_screen = True
                self._migrate_me_in_the_same_game = False
            self._state = STATE_MOVE_UP_OUT_OF_SCREEN

    def _move_freely(self):
        if self._new_direction != NONE:
            delta = self._length_to_next_block_based_on_direction(self._current_direction)
            if abs(delta) < self.speed:
                if self._is_there_wall_in_direction(self._new_direction):
                    self._move(self._current_direction)
                else:
                    self._x_move, self._y_move = self._get_speed(abs(delta), self._current_direction)
                    self._current_direction = self._new_direction
                    self._new_direction = NONE
            else:
                self._move(self._current_direction)
        elif self._current_direction != NONE:
            self._move(self._current_direction)

    def _move_left_of_screen(self):
        if self._migrate_me_to_another_screen:
            self._build_migrate_package(x=self._res[0] - self.speed, y=self._sprite_object.rect.y)
        self._x_move, self._y_move = self._get_speed(self.speed, LEFT)
        if self._sprite_object.rect.x + self._sprite_object.rect.w <= 0:
            if self._migrate_me_in_the_same_game:
                self._build_migrate_package(x=self._res[0] - self.speed, y=self._sprite_object.rect.y)
            else:
                self.delete_me = True

    def _move_right_of_screen(self):
        if self._migrate_me_to_another_screen:
            self._build_migrate_package(x=-self._sprite_object.rect.w + self.speed, y=self._sprite_object.rect.y)
        self._x_move, self._y_move = self._get_speed(self.speed, RIGHT)
        if self._sprite_object.rect.x >= self._res[0]:
            if self._migrate_me_in_the_same_game:
                self._build_migrate_package(x=-self._sprite_object.rect.w + self.speed, y=self._sprite_object.rect.y)
            else:
                self.delete_me = True

    def _move_down_of_screen(self):
        if self._migrate_me_to_another_screen:
            self._build_migrate_package(x=self._sprite_object.rect.x, y=-self._sprite_object.rect.h + self.speed)
        self._x_move, self._y_move = self._get_speed(self.speed, DOWN)
        if self._sprite_object.rect.y >= self._res[1]:
            if self._migrate_me_in_the_same_game:
                self._build_migrate_package(x=self._sprite_object.rect.x, y=-self._sprite_object.rect.h + self.speed)
            else:
                self.delete_me = True

    def _move_up_of_screen(self):
        if self._migrate_me_to_another_screen:
            self._build_migrate_package(x=self._sprite_object.rect.x, y=self._res[1] - self.speed)
        self._x_move, self._y_move = self._get_speed(self.speed, UP)
        if self._sprite_object.rect.y + self._sprite_object.rect.h <= 0:
            if self._migrate_me_in_the_same_game:
                self._build_migrate_package(x=self._sprite_object.rect.x, y=self._res[1] - self.speed)
            else:
                self.delete_me = True

    def _build_migrate_package(self, x, y):
        self._migrate_me_to_another_screen = False
        self.migrate[
            self._current_direction](pos_x=x,
                                     pos_y=y,
                                     current_direction=self.current_direction,
                                     new_direction=self._new_direction,
                                     name=self._name,
                                     map_x=self._x,
                                     map_y=self._y,
                                     color=self._color,
                                     sprite_x=self._sprite_object.x,
                                     sprite_y=self._sprite_object.y,
                                     speed_level=self.speed_level)

    def _migrate(self, **kwargs):
        self._sprite_object.rect.x = kwargs["pos_x"]
        self._sprite_object.rect.y = kwargs["pos_y"]
        self._state = STATE_MOVE_FREELY

    @property
    def current_direction(self):
        return [None, "left", "right", "up", "down"][self._current_direction]

    @property
    def sprite_object(self):
        return self._sprite_object

    def __str__(self):
        return "name:\t{name}\n" \
               "current_dir:\t{current_dir}\n" \
               "new_dir:\t{new_dir}\n" \
               "state:\t{state}\n".format(name=self._name, current_dir=self.current_direction,
                                        new_dir=self._new_direction,
                                        state=self._state)