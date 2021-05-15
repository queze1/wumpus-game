"""This module provides access to several classes that are associated with the player character."""

import pygame
from lib.helpers import Direction


PLAYER_MOVE_SPEED = 10
BULLET_MOVE_SPEED = 20
KEY_TO_DIR = {pygame.K_w: Direction.UP,
              pygame.K_a: Direction.LEFT,
              pygame.K_s: Direction.DOWN,
              pygame.K_d: Direction.RIGHT}
ARROW_TO_DIR = {pygame.K_UP: Direction.UP,
                pygame.K_LEFT: Direction.LEFT,
                pygame.K_DOWN: Direction.DOWN,
                pygame.K_LEFT: Direction.LEFT}


class Player(pygame.sprite.Sprite):
    def __init__(self, center=(0, 0)):
        super().__init__()
        self.image = pygame.image.load('assets/stevencrowder.jpg').convert()
        self.rect = self.image.get_rect(center=center)

        self.attack_delay = 20
        self.current_attack_delay = 0
        self.friendly_bullets = pygame.sprite.Group()

    def update(self):
        x = 0
        y = 0
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_w]:
            y -= 10
        if keys_pressed[pygame.K_s]:
            y += 10
        if keys_pressed[pygame.K_d]:
            x += 10
        if keys_pressed[pygame.K_a]:
            x -= 10

        # If the player is moving diagonally, divide their speeds by sqrt(2) to keep the speed the same
        if x and y:
            x /= 2 ** 0.5
            y /= 2 ** 0.5

        self.rect.move_ip(x, y)

        self.current_attack_delay -= 1
        if self.current_attack_delay <= 0:
            self.current_attack_delay = self.attack_delay

            #bullet = Bullet()
            #self.friendly_bullets.add(bullet)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, center=(0, 0)):
        super().__init__()
        self.image = pygame.image.load('assets/bullet.jpg').convert()
        self.rect = self.image.get_rect(center=center)

    def update(self):
        pass
