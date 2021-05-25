from random import randint

import pygame

from config import WINDOW_HEIGHT, WINDOW_WIDTH
from lib.helpers import BaseSprite


class EnemySpawner:
    def __init__(self, difficulty, lvl_number):
        self.difficulty = difficulty
        self.lvl_number = lvl_number
        self.enemies = pygame.sprite.Group()

    def spawn_enemies(self):
        self.enemies.add(TestEnemy((randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT))))

    def reset_enemies(self):
        self.enemies.empty()

class TestEnemy(BaseSprite):
    def __init__(self, center=(0, 0)):
        super().__init__(image_path='assets/bullets.png')
        self.rect = self.image.get_rect(center=center)
