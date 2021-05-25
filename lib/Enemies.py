from random import randint

import pygame

from config import WINDOW_HEIGHT, WINDOW_WIDTH


class EnemySpawner:
    def __init__(self, difficulty, lvl_number):
        self.difficulty = difficulty
        self.lvl_number = lvl_number
        self.enemies = pygame.sprite.Group()

    def spawn_enemies(self):
        self.enemies.add(TestEnemy((randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT))))

    def reset_enemies(self):
        self.enemies.empty()

class TestEnemy(pygame.sprite.Sprite):
    def __init__(self, center=(0,0)):
        super().__init__()
        self.image = pygame.image.load('assets/bullets.png').convert()
        self.rect = self.image.get_rect(center=center)
