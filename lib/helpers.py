"""
This module provides access to several useful constants, helper functions and classes.
"""

import pygame

import config


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
    UP_LEFT_DOWN_RIGHT = [UP, LEFT, DOWN, RIGHT]  # WASD


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, image_path=None, center=(0, 0)):
        super().__init__()
        if image_path:
            self.image = pygame.image.load(image_path).convert()
        self.rect = self.image.get_rect(center=center)


WINDOW_RECT = pygame.Rect(0, 0, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
