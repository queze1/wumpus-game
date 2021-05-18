"""This module provides access to several classes that are associated with the player character."""

import pygame

from lib.helpers import Direction, WINDOW_RECT
from lib.Obstacles import Wall

PLAYER_MOVE_SPEED = 5
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

    def collision_test(self, all_sprites, sprite_check):
        return [sprite for sprite in 
                pygame.sprite.spritecollide(self, all_sprites, False) 
                if isinstance(sprite, sprite_check)]

    def update(self, all_sprites):
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

        self.rect.y += y
        for wall in self.collision_test(all_sprites, Wall):
            if y > 0: 
                self.rect.bottom = wall.rect.top
            if y < 0:
                self.rect.top = wall.rect.bottom

        self.rect.x += x        
        for wall in self.collision_test(all_sprites, Wall):
            if x > 0: 
                self.rect.right = wall.rect.left
            if x < 0:
                self.rect.left = wall.rect.right

        # Shoot bullets
        self.current_attack_delay -= 1
        arrow_keys_pressed = [key for key in ARROW_TO_DIR if keys_pressed[key]]
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

    def update(self, all_sprites):
        x, y = self.dir * BULLET_MOVE_SPEED
        self.rect.move_ip(x, y)
