from random import randint

import pygame

from config import WINDOW_HEIGHT, WINDOW_WIDTH
from lib.helpers import BaseSprite


class BaseEnemy(BaseSprite):
    """Used to check if a sprite is an enemy or not."""


class TestEnemy(BaseEnemy):
    def __init__(self, center=(0, 0)):
        super().__init__(image_path='assets/enemy.png', center=center)


class TestBoss(BaseEnemy):
    def __init__(self, center=(0, 0)):
        super().__init__(image_path='assets/cat.png', center=center)
