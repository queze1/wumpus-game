"""This module provides access to several environmental object classes."""

from lib.helpers import BaseSprite


class Wall(BaseSprite):
    def __init__(self, center=(0, 0)):
        super().__init__(image_path='assets/wall.png', center=center)
