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

def strip_from_sheet(sheet, start, size, columns, rows=1):
    """
    Strips individual frames from a sprite sheet given a start location,
    sprite size, and number of columns and rows.
    """
    frames = []
    for j in range(rows):
        for i in range(columns):
            location = (start[0]+size[0]*i, start[1]+size[1]*j)
            image = sheet.subsurface(pygame.Rect(location, size))
            image = pygame.transform.scale(image, (64,64))
            frames.append(image)
    return frames

class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, image_assets=None, center=(0, 0)):
        super().__init__()
        self.flip = False
        self.state = 'idle'
        self.animation_frame = 0
        self.animation_frames = {}

        if isinstance(image_assets, str):
            self.image = pygame.image.load(image_assets).convert()
        elif isinstance(image_assets, list):
#           image_assets = [('idle', 'assets/player/player_idle.png', [7,7]),
#                           ('walking', 'assets/player/player_walking.png', [7,7,40])]
            self.load_animation(image_assets)
            self.image = self.animation_frames[self.image_assets[self.state][self.animation_frame]]

        self.rect = self.image.get_rect(center=center)

    def update_animation(self):
        self.animation_frame +=1
        if self.animation_frame >= len(self.image_assets[self.state]):
            self.animation_frame = 0
        self.image = self.animation_frames[self.image_assets[self.state][self.animation_frame]]
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = pygame.transform.flip(self.image, False, False)

    def load_animation(self, image_assets):
        self.image_assets = {}
        for image in image_assets:
            sprites = strip_from_sheet(pygame.image.load(image[1]), (0,0), (32,32), 4)
            self.animation_frames.update({f'{image[0]}_{sprites.index(sprite) + 1}' : sprite for sprite in sprites})
            print(self.animation_frames)

            self.image_assets[image[0]] = []
            x = 1
            for frame_count in image[2]:    
                for _ in range(0, frame_count):
                    self.image_assets[image[0]].append(f'{image[0]}_{x}')
                x += 1

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

def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame            

WINDOW_RECT = pygame.Rect(0, 0, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
