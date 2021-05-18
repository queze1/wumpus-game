"""This module provides access to several classes that are associated with the player character."""

import pygame

from lib.helpers import Direction, WINDOW_RECT

PLAYER_MOVE_SPEED = 8
BULLET_MOVE_SPEED = 20

KEY_TO_DIR = {pygame.K_w: Direction.UP,
              pygame.K_a: Direction.LEFT,
              pygame.K_s: Direction.DOWN,
              pygame.K_d: Direction.RIGHT}

ARROW_TO_DIR = {pygame.K_UP: Direction.UP,
                pygame.K_LEFT: Direction.LEFT,
                pygame.K_DOWN: Direction.DOWN,
                pygame.K_RIGHT: Direction.RIGHT}


class Player(pygame.sprite.Sprite):
    def __init__(self, center=(0, 0)):
        super().__init__()
        self.image = pygame.image.load('assets/stevencrowder.png').convert()
        self.rect = self.image.get_rect(center=center)

        self.attack_delay = 20
        self.current_attack_delay = 0
        self.friendly_bullets = pygame.sprite.Group()

    def handle_collisions(self):
        pass

    def update(self):
        # Movement
        x, y = 0, 0
        keys_pressed = pygame.key.get_pressed()
        for key in KEY_TO_DIR:
            if keys_pressed[key]:
                # MultiplicableTuple makes multiplying the tuple multiply everything inside of it instead
                x_change, y_change = KEY_TO_DIR[key] * PLAYER_MOVE_SPEED
                x += x_change
                y += y_change
        # If the player is moving diagonally, divide their speeds by sqrt(2) to keep the speed the same
        if x and y:
            x /= 2 ** 0.5
            y /= 2 ** 0.5

        self.handle_collisions()

        self.rect.move_ip(x, y)

        # Shoot bullets
        self.current_attack_delay -= 1
        arrow_keys_pressed = [key for key in ARROW_TO_DIR if keys_pressed[key]]
        # Currently only fire if only one arrow key is being pressed
        if self.current_attack_delay <= 0 and len(arrow_keys_pressed) == 1: 
            self.current_attack_delay = self.attack_delay
            bullet_dir = ARROW_TO_DIR[arrow_keys_pressed[0]]
            bullet = Bullet(bullet_dir, center=self.rect.center)
            self.friendly_bullets.add(bullet)

        # Erase bullets that are off the screen
        for bullet in self.friendly_bullets:
            if not bullet.rect.colliderect(WINDOW_RECT):
                bullet.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, dir, center=(0, 0)):
        super().__init__()
        self.dir = dir
        self.image = pygame.image.load('assets/bullets.png').convert()
        self.rect = self.image.get_rect(center=center)

    def update(self):
        x, y = self.dir * BULLET_MOVE_SPEED
        self.rect.move_ip(x, y)
