#!/usr/bin/env python
# -*- coding: utf8 -*-

# Forked From https://github.com/CaffeinatedTech/Python_Nibbles
# Written by CaffeinatedTech

# New Fork:
# Developed by mehrdad-mixtape https://github.com/mehrdad-mixtape/Snake_Game_Pyxel

# Python Version 3.6 or higher
# Snake Game

__repo__ = 'https://github.com/mehrdad-mixtape/Snake_Game_Pyxel'
__version__ = 'v0.1.1'

import pyxel, sys
from enum import Enum
from time import time
from typing import List
from random import randrange
from collections import deque

W = 8
H = 8
INCREASE_LEN_SNAKE = 2
GAME_NAME = "Snake Game-Pyxel"

def run(cls_game):
    def __runner__():
        game = cls_game()
        game.run()
    return __runner__

# Snake Direction labels
class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3

# Game state labels
class Game_state(Enum):
    RUNNING = 0
    GAME_OVER = 1

# Level class handles drawing the level (walls)
class Level:
    def __init__(self):
        self.tile_map = 0
        self.u = 0
        self.v = 0
        self.w = 24 * W
        self.h = 16 * H

    def draw(self):
        pyxel.bltm(0, 0, self.tile_map, self.u, self.v, self.w, self.h)

# Apple class handles drawing and moving the apple, as well as
# checking if anything is on the apple (snake ate it)
class Apple:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y
        self.__w = W
        self.__h = H

    def draw(self) -> None:
        pyxel.blt(self._x, self._y, 0, 16, 0, self.__w, self.__h)
    
    def intersects(self, u, v, w, h) -> bool:
        is_intersected = False
        if (
            u + w > self._x
            and self._x + self.__w > u
            and v + h > self._y
            and self._y + self.__h > v
        ):
            is_intersected = True
        return is_intersected
    
    def move(self, new_x: int, new_y: int) -> None:
        self._x = new_x
        self._y = new_y

# Snake class handles drawing snake sections including orienting the head
# Also checking if something intersects it (snake crashed into itself or walls)
class Snake:
    def __init__(self, x: int, y: int, is_head: bool=False):
        self._x = x
        self._y = y
        self.__w = W
        self.__h = H
        self._is_head = is_head

    def draw(self, direction: Direction) -> None:
        width = self.__w
        height = self.__h
        sprite_x = 0
        sprite_y = 0
        # If this the head section, then we need to change and flip the sprite depending on the direction.
        if self._is_head:
            if direction == Direction.RIGHT:
                sprite_x = 8
                sprite_y = 0
            elif direction == Direction.LEFT:
                sprite_x = 8
                sprite_y = 0
                width *= -1
            elif direction == Direction.DOWN:
                sprite_x = 0
                sprite_y = 8
            if direction == Direction.UP:
                sprite_x = 0
                sprite_y = 8
                height *= -1
        
        pyxel.blt(self._x, self._y, 0, sprite_x, sprite_y, width, height)

    @property
    def x(self) -> int:
        return self._x
    @x.setter
    def x(self, value: int) -> None:
        self._x = value
    
    @property
    def y(self) -> int:
        return self._y
    @y.setter
    def y(self, value: int) -> None:
        self._y = value

    def intersects(self, u, v, w, h) -> bool:
        is_intersected = False
        if (
            u + w > self._x
            and self._x + self.__w > u
            and v + h > self._y
            and self._y + self.__h > v
        ):
            is_intersected = True
        return is_intersected

# Hud class handles drawing text and scores
class Hud:
    def __init__(self):
        self.title_text = GAME_NAME
        self.title_text_x = self.center_text(self.title_text, 196)
        self.score_text = str(0)
        self.score_text_x = self.right_text(self.score_text, 196)
        self.level_text = "Level 0"
        self.level_text_x = 10
        self.apples_text = "Apples "
        self.apples_text_x = len(self.level_text) * pyxel.FONT_WIDTH + self.level_text_x + 5
    
    def draw_title(self) -> None:
        pyxel.rect(self.title_text_x - 1, 0, len(self.title_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.title_text_x, 1, self.title_text, 12)

    def draw_score(self, score: int) -> None:
        self.score_text = f"Score {score}"
        self.score_text_x = self.right_text(self.score_text, 196)
        pyxel.rect(self.score_text_x - 11, 0, len(self.score_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.score_text_x - 10, 1, self.score_text, 3)

    def draw_level(self, level: int) -> None:
        self.level_text = f"Level {level}"
        pyxel.rect(self.level_text_x - 1, 0, len(self.level_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.level_text_x, 1, self.level_text, 3)

    def draw_apples(self, apples) -> None:
        self.apples_text = f"Apples {apples}"
        pyxel.rect(self.apples_text_x - 34, 121, len(self.apples_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.apples_text_x - 33, 122, self.apples_text, 8)
    
    def center_text(self, text: str, page_width, char_width=pyxel.FONT_WIDTH) -> None:
        text_width = len(text) * char_width
        return (page_width - text_width) / 2

    def right_text(self, text: str, page_width, char_width=pyxel.FONT_WIDTH) -> None:
        text_width = len(text) * char_width
        return page_width - (text_width + char_width)

@run
class Snake_Game_App:
    def __init__(self):
        pyxel.init(192, 128, display_scale=8, title=GAME_NAME, fps=60) # Create a display.
        pyxel.load("./assets/snake_assets.pyxres") # Load assets.

        self.current_state = Game_state.RUNNING

        self.level = Level() # Make level

        self.hud = Hud()

        self.apple = Apple(64, 32) # Make apple.
        self.snake: List[Snake] = [Snake(32, 32, is_head=True), Snake(24, 32), Snake(16, 32)] # Make snake.
        self.snake_direction: Direction = Direction.RIGHT # Set direction.

        self.sections_to_add = 0

        self.speed = 1.5 # Speed of game
        self.time_last_frame = time()
        self.dt = 0 # Delta time
        self.time_since_last_move = 0
        
        self.score = 0
        self.apples_eaten_total = 0
        self.current_level = 1

        self.input_queue = deque() # Store the direction changes so the player can easily chain them

        self.play_music = True
        if self.play_music:
            pyxel.playm(0, loop=True) # Play music

    def run(self) -> None:
        pyxel.run(self.update, self.draw) # Run the app

    def start_new_game(self):
        self.current_state = Game_state.RUNNING
        self.snake.clear()
        # Add initial snake to the game
        self.snake: List[Snake] = [Snake(32, 32, is_head=True), Snake(24, 32), Snake(16, 32)] # Make snake.
        self.snake_direction: Direction = Direction.RIGHT # Set direction.

        self.sections_to_add = 0

        self.speed = 1.5 # Speed of game
        self.time_last_frame = time()
        self.dt = 0 # Delta time
        self.time_since_last_move = 0

        self.score = 0
        self.apples_eaten_total = 0
        self.current_level = 1

        self.input_queue.clear()

        self.move_apple()

        if self.play_music:
            pyxel.playm(0, loop=True)

    def update(self) -> None:
        # self.x = (self.x + 1) % pyxel.width
        time_this_frame = time()
        self.dt = time_this_frame - self.time_last_frame
        self.time_last_frame = time_this_frame
        self.time_since_last_move += self.dt
        self.check_input()
        if self.current_state == Game_state.RUNNING:
            if self.time_since_last_move >= 1 / self.speed:
                self.time_since_last_move = 0
                self.move_snake()
                self.check_collisions()
                self.score = len(self.snake) * self.apples_eaten_total + 1
    
    def toggle_music(self):
        if self.play_music:
            self.play_music = False
            pyxel.stop() # Stop all sound
        else:
            self.play_music = True
            pyxel.playm(0, loop=True) # Play music

    def draw(self) -> None:
        pyxel.cls(0) # Clear display.
        # pyxel.rect(self.x, 0, 10, 4, 11) # rect(x, y, width, height, color)
        self.level.draw()
        self.apple.draw() # Draw Apple
        for s in self.snake: s.draw(self.snake_direction) # Draw Snake
        self.hud.draw_title()
        self.hud.draw_level(self.current_level)
        self.hud.draw_score(self.score)
        self.hud.draw_apples(self.apples_eaten_total)
        pyxel.text(18, 114, str(self.current_state), 11)
        if self.current_state == Game_state.GAME_OVER:
            pyxel.cls(0)
            self.level.draw()
            self.hud.draw_title()
            self.hud.draw_level(self.current_level)
            self.hud.draw_score(self.score)
            self.hud.draw_apples(self.apples_eaten_total)
            pyxel.text(18, 114, str(self.current_state), 8)
            pyxel.text(40, 64, "Press Enter to Start New Game", 12)

    def check_collisions(self) -> None:
        # Apple:
        if self.apple.intersects(self.snake[0].x, self.snake[0].y, W, H):
            pyxel.play(3, 0)
            self.speed += (self.speed * 0.05)
            self.sections_to_add += INCREASE_LEN_SNAKE
            self.move_apple()
            self.apples_eaten_total += 1
        
        # Snake tail:
        for s in self.snake:
            if s == self.snake[0]:
                continue
            if s.intersects(self.snake[0].x, self.snake[0].y, W, H):
                pyxel.stop()
                pyxel.play(3, 1)
                self.current_state = Game_state.GAME_OVER
        
        # Wall:
        if pyxel.tilemap(0).pget(self.snake[0].x / 8, self.snake[0].y / 8)[0] == 3:
            pyxel.stop()
            pyxel.play(3, 1)
            self.current_state = Game_state.GAME_OVER

    def move_apple(self) -> None:
        # Select a new random location for the apple.
        # Make sure it is not in a wall, or in the snake.
        good_position = False
        while not good_position:
            new_x = randrange(8, 180, 8)
            new_y = randrange(8, 110, 8)
            good_position = True
            # Check snake:
            for s in self.snake:
                if (
                    new_x + 8 > s.x
                    and s.x + W > new_x
                    and new_y + 8 > s.y
                    and s.y + H > new_y
                ):
                    good_position = False
                    break
            # TODO: Check Wall:

            # If the position is good, move the apple
            if good_position:
                self.apple.move(new_x, new_y)

    def move_snake(self) -> None:
        # Do We need to change direction?
        if len(self.input_queue):
            self.snake_direction = self.input_queue.popleft()
        # Do we need to grow the snake?
        if self.sections_to_add > 0:
            self.snake.append(Snake(self.snake[-1].x, self.snake[-1].y))
            self.sections_to_add -= 1
        # Move the head:
        previous_loc_x = self.snake[0].x
        previous_loc_y = self.snake[0].y
        if self.snake_direction == Direction.RIGHT:
            # self.snake[0].x = (self.snake[0].x + W) % pyxel.width
            self.snake[0].x += W
        elif self.snake_direction == Direction.LEFT:
            # self.snake[0].x = (self.snake[0].x - W) % pyxel.width
            self.snake[0].x -= W
        elif self.snake_direction == Direction.DOWN:
            # self.snake[0].y = (self.snake[0].y + H) % pyxel.height
            self.snake[0].y += H
        elif self.snake_direction == Direction.UP:
            # self.snake[0].y = (self.snake[0].y - H) % pyxel.height
            self.snake[0].y -= H
        
        # Move the tail:
        for s in self.snake:
            if s == self.snake[0]:
                continue
            current_loc_x = s.x
            current_loc_y = s.y

            s.x = previous_loc_x
            s.y = previous_loc_y

            previous_loc_x = current_loc_x
            previous_loc_y = current_loc_y

    def check_input(self) -> None:
        if self.current_state == Game_state.GAME_OVER:
            if pyxel.btn(pyxel.KEY_RETURN):
                self.start_new_game()

        if pyxel.btnp(pyxel.KEY_M):
            self.toggle_music()

        if pyxel.btn(pyxel.KEY_ESCAPE):
            sys.exit()

        if pyxel.btn(pyxel.KEY_RIGHT):
            if len(self.input_queue) == 0:
                if (
                    self.snake_direction != Direction.LEFT
                    and self.snake_direction != Direction.RIGHT
                ): self.input_queue.append(Direction.RIGHT)
            else:
                if (
                    self.input_queue[-1] != Direction.LEFT
                    and self.input_queue[-1] != Direction.RIGHT
                ): self.input_queue.append(Direction.RIGHT)
        
        elif pyxel.btn(pyxel.KEY_LEFT):
            if len(self.input_queue) == 0:
                if (
                    self.snake_direction != Direction.RIGHT
                    and self.snake_direction != Direction.LEFT
                ): self.input_queue.append(Direction.LEFT)
            else:
                if (
                    self.input_queue[-1] != Direction.RIGHT
                    and self.input_queue[-1] != Direction.LEFT
                ): self.input_queue.append(Direction.LEFT)
        
        elif pyxel.btn(pyxel.KEY_DOWN):
            if len(self.input_queue) == 0:
                if (
                    self.snake_direction != Direction.UP
                    and self.snake_direction != Direction.DOWN
                ): self.input_queue.append(Direction.DOWN)
            else:
                if (
                    self.input_queue[-1] != Direction.UP
                    and self.input_queue[-1] != Direction.DOWN
                ): self.input_queue.append(Direction.DOWN)
        
        elif pyxel.btn(pyxel.KEY_UP):
            if len(self.input_queue) == 0:
                if (
                    self.snake_direction != Direction.DOWN
                    and self.snake_direction != Direction.UP
                ): self.input_queue.append(Direction.UP)
            else:
                if (
                    self.input_queue[-1] != Direction.DOWN
                    and self.input_queue[-1] != Direction.UP
                ): self.input_queue.append(Direction.UP)

def main():
    Snake_Game_App()

if __name__ == '__main__':
    main()