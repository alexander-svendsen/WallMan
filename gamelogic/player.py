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
    def __init__(self, sprite_rect, name, layout, res, connection, speed=2):
        self.speed_level = speed
        self.speed = (sprite_rect.rect.w + sprite_rect.rect.h) * self.speed_level / 20

        assert self.speed <= sprite_rect.rect.w, "Speed can never be greater then the width of the player"
        assert self.speed <= sprite_rect.rect.h, "Speed can never be greater then the height of the player"

        self.connection = connection

        self.x_move = 0
        self.y_move = 0
        self.res = res

        self.name = name

        self.current_direction = NONE
        self.new_direction = NONE
        self._sprite_rect = sprite_rect
        self.color = sprite_rect.color

        self._movement_converter_dict = {"left": 1,
                                         "right": 2,
                                         "up": 3,
                                         "down": 4}

        #The position in the layout. Set in the update method
        self.x = 0
        self.y = 0

        # To helper directions to decide which path to take
        self.xDirection = [0, -self.speed, self.speed, 0, 0]
        self.yDirection = [0, 0, 0, -self.speed, self.speed]

        self.layout = layout
        self.layout_height = len(layout)
        self.layout_width = len(layout[0])
        self.state = STATE_MOVE_FREELY

        self.migrate_me = False

    def update_movement(self, direction):
        self.new_direction = self._movement_converter_dict[direction.lower()]
        if self.current_direction == NONE:
            self.current_direction = self.new_direction
            self.new_direction = NONE

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
            length = self._length_to_next_block(self.x, self._sprite_rect.rect.w, self._sprite_rect.rect.x)
            if length <= 0:
                return length
        elif direction == RIGHT:
            length = self._length_to_next_block(self.x, self._sprite_rect.rect.w, self._sprite_rect.rect.x)
            if length >= 0:
                return length
        elif direction == UP:
            length = self._length_to_next_block(self.y, self._sprite_rect.rect.h, self._sprite_rect.rect.y)
            if length <= 0:
                return length
        elif direction == DOWN:
            length = self._length_to_next_block(self.y, self._sprite_rect.rect.h, self._sprite_rect.rect.y)
            if length >= 0:
                return length
        return self.speed

    def _next_block(self, x, y, direction):
        return [0, (y, x - 1), (y, x + 1), (y - 1, x), (y + 1, x)][direction]

    def _is_there_wall_in_direction(self, direction):
        next_block = self._next_block(self.x, self.y, direction)
        return self._is_wall(*next_block)

    def _get_speed(self, speed, direction):
        return [0, -speed, speed, 0, 0][direction], [0, 0, 0, -speed, speed][direction]

    def _move(self, direction, speed):
        self.x_move, self.y_move = self._get_speed(self.speed, direction)
        if self._is_there_wall_in_direction(direction):
            length = self._length_to_next_block_based_on_direction(direction)
            if abs(length) >= speed:
                self.x_move, self.y_move = self._get_speed(speed, direction)
            else:
                self.x_move, self.y_move = self._get_speed(abs(length), direction)

    def _calculate_current_position_in_layout(self):
        self.x = self._sprite_rect.rect.center[0] / self._sprite_rect.rect.w
        self.y = self._sprite_rect.rect.center[1] / self._sprite_rect.rect.h

    def update(self, spriteFloor):
        self._calculate_current_position_in_layout()
        self._update_state_of_player()

        if self.state == STATE_MOVE_FREELY:  # review: may remove the switch case to a dict
            if self.new_direction != NONE:
                delta = self._length_to_next_block_based_on_direction(self.current_direction)
                if abs(delta) < self.speed:
                    if self._is_there_wall_in_direction(self.new_direction):
                        restSpeed = self._get_speed(self.speed - abs(delta), self.current_direction)
                        self._move(self.current_direction, restSpeed)
                    else:
                        self.x_move, self.y_move = self._get_speed(abs(delta), self.current_direction)
                        self.current_direction = self.new_direction
                        self.new_direction = NONE
                else:
                    self._move(self.current_direction, self.speed)
            elif self.current_direction != NONE:
                self._move(self.current_direction, self.speed)
            self._check_floor_collision(spriteFloor)
        elif self.state == STATE_MOVE_RIGHT_OUT_OF_SCREEN:
            self._move_right_of_screen()
        elif self.state == STATE_MOVE_LEFT_OUT_OF_SCREEN:
            self._move_left_of_screen()
        elif self.state == STATE_MOVE_DOWN_OUT_OF_SCREEN:
            self._move_down_of_screen()
        elif self.state == STATE_MOVE_UP_OUT_OF_SCREEN:
            self._move_up_of_screen()
        else:
            raise Exception("Invalid state of player, Should never happen")

        self._sprite_rect.rect.move_ip(self.x_move, self.y_move)

    def _check_floor_collision(self, spriteFloor):
        # TODO refactor out collision
        floorCollide = pygame.sprite.spritecollide(self._sprite_rect, spriteFloor, False)
        if floorCollide:
            for floor in floorCollide:
                floor.mark(self.color, self.name)

    def _update_state_of_player(self):
        if self.x + 1 >= self.layout_width and self.current_direction == RIGHT:
            self.state = STATE_MOVE_RIGHT_OUT_OF_SCREEN
        elif self.x - 1 < 0 and self.current_direction == LEFT:
            self.state = STATE_MOVE_LEFT_OUT_OF_SCREEN
        elif self.y + 1 >= self.layout_height and self.current_direction == DOWN:
            self.state = STATE_MOVE_DOWN_OUT_OF_SCREEN
        elif self.y - 1 < 0 and self.current_direction == UP:
            self.state = STATE_MOVE_UP_OUT_OF_SCREEN

    def _move_left_of_screen(self):
        self.x_move, self.y_move = self._get_speed(self.speed, LEFT)
        if self._sprite_rect.rect.x + self._sprite_rect.rect.w <= 0:
            self.connection.sendPlayerInDirection('left', self.new_direction, self.name, self.x, self.y, self.color, self._sprite_rect.id, self._sprite_rect.inverse_color)
            #self.spriteRect.rect.x = self.res[0] - self.speed
            #self.state = STATE_MOVEFREELY
            self.migrate_me = True

    def _move_right_of_screen(self):
        self.x_move, self.y_move = self._get_speed(self.speed, RIGHT)
        if self._sprite_rect.rect.x >= self.res[0]:
            self.connection.sendPlayerInDirection('right', self.new_direction, self.name, self.x, self.y, self.color, self._sprite_rect.id, self._sprite_rect.inverse_color)
            #self.spriteRect.rect.x = - self.spriteRect.rect.w + self.speed
            #self.state = STATE_MOVEFREELY
            self.migrate_me = True

    def _move_down_of_screen(self):
        self.x_move, self.y_move = self._get_speed(self.speed, DOWN)
        if self._sprite_rect.rect.y >= self.res[1]:
            self.connection.sendPlayerInDirection('down', self.new_direction, self.name, self.x, self.y, self.color, self._sprite_rect.id, self._sprite_rect.inverse_color)
            #self.spriteRect.rect.y = - self.spriteRect.rect.h + self.speed
            #self.state = STATE_MOVEFREELY
            self.migrate_me = True

    def _move_up_of_screen(self):
        self.x_move, self.y_move = self._get_speed(self.speed, UP)
        if self._sprite_rect.rect.y + self._sprite_rect.rect.h <= 0:
            self.connection.sendPlayerInDirection('up', self.new_direction, self.name, self.x, self.y, self.color, self._sprite_rect.id, self._sprite_rect.inverse_color)
            #self.spriteRect.rect.y = self.res[1] - self.speed
            #self.state = STATE_MOVEFREELY
            self.migrate_me = True

    @property
    def sprite_rect(self):
        return self._sprite_rect
