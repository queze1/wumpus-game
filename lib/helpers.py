"""
This module provides access to several useful constants, helper functions and classes.
"""

import pygame

import config
from lib.Obstacles import Wall


class MultiplicableTuple(tuple):
    """A tuple, but when it is multiplied by an integer it multiplies all the items in it instead."""
    def __mul__(self, other):
        if isinstance(other, int):
            return MultiplicableTuple([item*other for item in self])
        else:
            raise TypeError(f"can't multiply sequence by non-int of type '{type(self).__name__}'")


class Direction:
    UP = MultiplicableTuple([0, -1])
    DOWN = MultiplicableTuple([0, 1])
    LEFT = MultiplicableTuple([-1, 0])
    RIGHT = MultiplicableTuple([1, 0])
    UP_LEFT_DOWN_RIGHT = (UP, LEFT, DOWN, RIGHT)  # WASD


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, image_path=None, center=(0, 0)):
        super().__init__()
        if image_path:
            self.image = pygame.image.load(image_path).convert()
        self.rect = self.image.get_rect(center=center)

    def move_respecting_walls(self, x, y, all_sprites):
        walls = [sprite for sprite in all_sprites if isinstance(sprite, Wall)]
        self.rect.y += y
        for wall in pygame.sprite.spritecollide(self, walls, False):
            if y > 0:
                self.rect.bottom = wall.rect.top
            if y < 0:
                self.rect.top = wall.rect.bottom
        self.rect.x += x
        for wall in pygame.sprite.spritecollide(self, walls, False):
            if x > 0:
                self.rect.right = wall.rect.left
            if x < 0:
                self.rect.left = wall.rect.right


WINDOW_RECT = pygame.Rect(0, 0, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
