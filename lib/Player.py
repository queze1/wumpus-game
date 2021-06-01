"""This module provides access to several classes that are associated with the player character."""

import pygame

from lib.helpers import BaseSprite, Direction, WINDOW_RECT, change_action
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


class Player(BaseSprite):
    def __init__(self, center=(0, 0)):
        image_assets = [('idle', 'assets/player/player_idle.png', [40, 40, 40, 40]),
                        ('walking', 'assets/player/player_walking.png', [7, 7, 7, 7])]
        super().__init__(image_assets=image_assets, center=center)
        self.attack_delay = 20
        self.current_attack_delay = 0
        self.friendly_bullets = pygame.sprite.Group()

    def update(self, all_sprites, player):
        # Movement
        x, y = 0, 0
        keys_pressed = pygame.key.get_pressed()
        for key in KEY_TO_DIR:
            if keys_pressed[key]:
                x_change, y_change = KEY_TO_DIR[key] * PLAYER_MOVE_SPEED
                x += x_change
                y += y_change

        # If the player is moving diagonally, divide their speeds by sqrt(2) to keep the speed the same
        if x and y:
            x /= 2 ** 0.5
            y /= 2 ** 0.5

        # Move with wall collision
        self.move_respecting_walls(x, y, all_sprites)

        # Shoot bullets
        self.current_attack_delay -= 1
        arrow_keys_pressed = [key for key in ARROW_TO_DIR if keys_pressed[key]]
        # Currently only fire if only one arrow key is being pressed
        if self.current_attack_delay <= 0 and len(arrow_keys_pressed) == 1: 
            self.current_attack_delay = self.attack_delay
            bullet_dir = ARROW_TO_DIR[arrow_keys_pressed[0]]
            bullet = Bullet(bullet_dir, center=self.rect.center)
            self.friendly_bullets.add(bullet)

        # Animation
        if x > 0:
            self.flip = False
            self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'walking')
        elif abs(y) > 0:
            self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'walking')
        elif x < 0:
            self.flip = True
            self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'walking')
        else: 
            self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'idle')

        self.update_animation()


class Bullet(BaseSprite):
    def __init__(self, direction, center=(0, 0)):
        super().__init__(image_assets='assets/bullet.png', center=center)
        self.dir = direction

    def update(self, all_sprites, player):
        x, y = self.dir * BULLET_MOVE_SPEED
        self.rect.move_ip(x, y)

        # Erase the bullet if it hits a wall or goes offscreen
        walls = [sprite for sprite in all_sprites if isinstance(sprite, Wall)]
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
            return
        if not self.rect.colliderect(WINDOW_RECT):
            self.kill()
            return
