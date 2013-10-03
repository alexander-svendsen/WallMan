import pygame
import maps.config as gameLayoutConfig

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


class Player():
    def __init__(self, sprite_rect, name, layout, res, speed=2, **kwargs):
        self.speed_level = speed  # TODO actually use this
        self.speed = (sprite_rect.rect.w + sprite_rect.rect.h) * self.speed_level / 20

        assert self.speed <= sprite_rect.rect.w, "Speed can never be greater then the width of the player"
        assert self.speed <= sprite_rect.rect.h, "Speed can never be greater then the height of the player"

        #review # should be updates as the connection updates
        self.migrate = {LEFT: self._migrate if "left" not in kwargs else kwargs["left"],
                        RIGHT: self._migrate if "right" not in kwargs else kwargs["right"],
                        UP: self._migrate if "up" not in kwargs else kwargs["up"],
                        DOWN: self._migrate if "down" not in kwargs else kwargs["down"]}

        self.migrate_me = False
        self._x_move = 0
        self._y_move = 0
        self._res = res

        self._name = name

        self._current_direction = NONE
        self._new_direction = NONE
        self._sprite_rect = sprite_rect
        self._color = sprite_rect.color

        self._movement_converter_dict = {"none": NONE,
                                         "left": LEFT,
                                         "right": RIGHT,
                                         "up": UP,
                                         "down": DOWN}

        self._state_dict = {STATE_MOVE_FREELY: self._move_freely,
                            STATE_MOVE_DOWN_OUT_OF_SCREEN: self._move_down_of_screen,
                            STATE_MOVE_LEFT_OUT_OF_SCREEN: self._move_left_of_screen,
                            STATE_MOVE_RIGHT_OUT_OF_SCREEN: self._move_right_of_screen,
                            STATE_MOVE_UP_OUT_OF_SCREEN: self._move_up_of_screen}

        #The position in the layout. Set in the update method
        self._x = 0
        self._y = 0

        self.layout = layout  # review: remove, should be an input parameter in case the layout changes
        self.layout_height = len(layout)
        self.layout_width = len(layout[0])
        self._state = STATE_MOVE_FREELY

    def update_movement(self, direction):
        self._new_direction = self._movement_converter_dict[direction]
        if self._current_direction == NONE:
            self._current_direction = self._new_direction
            self._new_direction = NONE

    def _is_wall(self, y, x):
        if x >= self.layout_width or x < 0:
            return False
        if 0 > y or y >= self.layout_height:
            return False
        return self.layout[y][x] == gameLayoutConfig.BLOCK

    def _length_to_next_block(self, blockPos, playerSize, playerCoordinate):
        return blockPos * playerSize - playerCoordinate

    def _length_to_next_block_based_on_direction(self, direction):
        if direction == LEFT:
            length = self._length_to_next_block(self._x, self._sprite_rect.rect.w, self._sprite_rect.rect.x)
            if length <= 0:
                return length
        elif direction == RIGHT:
            length = self._length_to_next_block(self._x, self._sprite_rect.rect.w, self._sprite_rect.rect.x)
            if length >= 0:
                return length
        elif direction == UP:
            length = self._length_to_next_block(self._y, self._sprite_rect.rect.h, self._sprite_rect.rect.y)
            if length <= 0:
                return length
        elif direction == DOWN:
            length = self._length_to_next_block(self._y, self._sprite_rect.rect.h, self._sprite_rect.rect.y)
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

    def _move(self, direction, speed):
        self._x_move, self._y_move = self._get_speed(self.speed, direction)
        if self._is_there_wall_in_direction(direction):
            length = self._length_to_next_block_based_on_direction(direction)
            if abs(length) >= speed:
                self._x_move, self._y_move = self._get_speed(speed, direction)
            else:
                self._x_move, self._y_move = self._get_speed(abs(length), direction)

    def _calculate_current_position_in_layout(self):
        self._x = self._sprite_rect.rect.center[0] / self._sprite_rect.rect.w
        self._y = self._sprite_rect.rect.center[1] / self._sprite_rect.rect.h

    def update(self, floor_sprites):
        self._calculate_current_position_in_layout()
        self._update_state_of_player()

        self._state_dict[self._state]()

        self._check_floor_collision(floor_sprites)
        self._sprite_rect.rect.move_ip(self._x_move, self._y_move)

    def _check_floor_collision(self, sprite_floor):
        # TODO refactor out collision
        floorCollide = pygame.sprite.spritecollide(self._sprite_rect, sprite_floor, False)
        if floorCollide:
            for floor in floorCollide:
                floor.mark(self._color, self._name)

    def _update_state_of_player(self):
        if self._x + 1 >= self.layout_width and self._current_direction == RIGHT:
            self._state = STATE_MOVE_RIGHT_OUT_OF_SCREEN
        elif self._x - 1 < 0 and self._current_direction == LEFT:
            self._state = STATE_MOVE_LEFT_OUT_OF_SCREEN
        elif self._y + 1 >= self.layout_height and self._current_direction == DOWN:
            self._state = STATE_MOVE_DOWN_OUT_OF_SCREEN
        elif self._y - 1 < 0 and self._current_direction == UP:
            self._state = STATE_MOVE_UP_OUT_OF_SCREEN

    def _move_freely(self):
        if self._new_direction != NONE:
            delta = self._length_to_next_block_based_on_direction(self._current_direction)
            if abs(delta) < self.speed:
                if self._is_there_wall_in_direction(self._new_direction):
                    restSpeed = self._get_speed(self.speed - abs(delta), self._current_direction)
                    self._move(self._current_direction, restSpeed)
                else:
                    self._x_move, self._y_move = self._get_speed(abs(delta), self._current_direction)
                    self._current_direction = self._new_direction
                    self._new_direction = NONE
            else:
                self._move(self._current_direction, self.speed)
        elif self._current_direction != NONE:
            self._move(self._current_direction, self.speed)

    def _move_left_of_screen(self):
        self._x_move, self._y_move = self._get_speed(self.speed, LEFT)
        if self._sprite_rect.rect.x + self._sprite_rect.rect.w <= 0:
            self._build_migrate_package(x=self._res[0] - self.speed, y=self._sprite_rect.rect.y)

    def _move_right_of_screen(self):
        self._x_move, self._y_move = self._get_speed(self.speed, RIGHT)
        if self._sprite_rect.rect.x >= self._res[0]:
            self._build_migrate_package(x=-self.sprite_rect.rect.w + self.speed, y=self._sprite_rect.rect.y)

    def _move_down_of_screen(self):
        self._x_move, self._y_move = self._get_speed(self.speed, DOWN)
        if self._sprite_rect.rect.y >= self._res[1]:
            self._build_migrate_package(x=self._sprite_rect.rect.x, y=-self._sprite_rect.rect.h + self.speed)

    def _move_up_of_screen(self):
        self._x_move, self._y_move = self._get_speed(self.speed, UP)
        if self._sprite_rect.rect.y + self._sprite_rect.rect.h <= 0:
            self._build_migrate_package(x=self._sprite_rect.rect.x, y=self._res[1] - self.speed)

    def _build_migrate_package(self, x, y):
        self.migrate_me = True
        self.migrate[
            self._current_direction](pos_x=x,
                                     pos_y=y,
                                     current_direction=[None, "left", "right", "up", "down"][self._current_direction],
                                     new_direction=self._new_direction,
                                     name=self._name,
                                     layout_x=self._x,
                                     layout_y=self._y,
                                     color=self._color,
                                     askii=self._sprite_rect.id,
                                     askii_color=self.sprite_rect.inverse_color)

    def _migrate(self, **kwargs):
        self.migrate_me = False
        self._sprite_rect.rect.x = kwargs["pos_x"]
        self._sprite_rect.rect.y = kwargs["pos_y"]
        self._state = STATE_MOVE_FREELY

    @property
    def sprite_rect(self):
        return self._sprite_rect
