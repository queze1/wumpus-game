"""This module provides access to several environmental object classes."""

import pygame

# Do not import from lib.helpers because lib.helpers imports from here for easy collision detection


class Wall(pygame.sprite.Sprite):
    def __init__(self, center=(0, 0)):
        super().__init__()
        self.image = pygame.image.load('assets/wall.png').convert()
        self.rect = self.image.get_rect(center=center)

