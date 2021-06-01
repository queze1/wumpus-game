"""
This module provides access to several useful constants, helper functions and classes.
"""

import pygame

import config
from lib.Obstacles import Wall


class Vector(pygame.math.Vector2):
    def __eq__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        else:
            return False

    def __hash__(self):
        return hash((self.x, self.y))


class Direction:
    UP = Vector(0, -1)
    DOWN = Vector(0, 1)
    LEFT = Vector(-1, 0)
    RIGHT = Vector(1, 0)
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
            rect = image.get_rect()
            image = pygame.transform.scale(image, (rect.width * 2, rect.height * 2))
            frames.append(image)
    return frames


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, image_assets=None, center=(0, 0), alpha=False):
        super().__init__()
        self.flip = False
        self.state = 'idle'
        self.animation_frame = 0
        self.animation_frames = {}
        self.particles = pygame.sprite.Group()
        self.image_assets = {}

        if isinstance(image_assets, str):
            if not alpha:
                self.image = pygame.image.load(image_assets).convert()
            else:
                self.image = pygame.image.load(image_assets).convert_alpha()
        elif isinstance(image_assets, list):
            # image_assets = [('idle', 'assets/player/player_idle.png', [7,7], [width, height]),
            #                 ('walking', 'assets/player/player_walking.png', [7,7,40], [width, height])]
            self.load_animation(image_assets)
            self.image = self.animation_frames[self.image_assets[self.state][self.animation_frame]]

        if self.image:
            self.rect = self.image.get_rect(center=center)

    def update_animation(self):
        self.animation_frame += 1
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
            sprites = strip_from_sheet(pygame.image.load(image[1]), (0, 0), (image[3][0], image[3][1]), len(image[2]))
            self.animation_frames.update({f'{image[0]}_{sprites.index(sprite) + 1}': sprite for sprite in sprites})
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


def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


WINDOW_RECT = pygame.Rect(0, 0, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
