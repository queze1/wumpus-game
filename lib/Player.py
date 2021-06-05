"""This module provides access to several classes that are associated with the player character."""

from functools import partial

import pygame

from lib.Enemies import BaseEnemy, EnemyBullet
from lib.helpers import BaseSprite, change_action, euclidean_distance, Direction, WINDOW_RECT
from lib.Obstacles import Wall
from lib.Particles import ParticleSpawner


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


bullet_particles = {
    'velocity': ((-1, 1), (-1, 1)),
    'radius': (3, 5),
    'colour': (255, 236, 214),
    'decay': 0.4
}

damage_particles = {
    'velocity': ((-3,3), (-3,3)),
    'radius': (2,3),
    'colour': (255,236,214),
    'decay': 0.1
}


class Player(BaseSprite):
    def __init__(self, center=(0, 0)):
        image_assets = [('idle', 'assets/player/player_idle.png', [40, 40, 40, 40], (12, 32)),
                        ('walking', 'assets/player/player_walking.png', [15, 15, 15, 15, 15], (12, 32)),
                        ('damaged_idle', 'assets/player/player_damaged_idle.png', [7, 7, 7, 7], (12, 32)),
                        ('damaged_walking', 'assets/player/player_damaged_walking.png', [7, 7, 7, 7, 7], (12, 32))]
        super().__init__(image_assets=image_assets, center=center)
        self.hp = 5
        self.attack_delay = 20
        self.current_attack_delay = 0
        self.damage_delay = 100
        self.current_damage_delay = 0
        self.bullets = pygame.sprite.Group()

    def update(self, all_sprites, player, game_map):
        # Movement
        self.x_y = pygame.Vector2()
        keys_pressed = pygame.key.get_pressed()
        for key in KEY_TO_DIR:
            if keys_pressed[key]:
                self.x_y += KEY_TO_DIR[key]

        if self.x_y:
            self.x_y = self.x_y.normalize() * PLAYER_MOVE_SPEED
        x, y = self.x_y

        # Handle damage
        self.current_damage_delay -= 1
        if self.current_damage_delay <= 0:
            enemies = pygame.sprite.Group([sprite for sprite in all_sprites if isinstance(sprite, (BaseEnemy, EnemyBullet))])
            enemies_collided = pygame.sprite.spritecollide(self, enemies, False)
            if enemies_collided:
                self.particles.add(ParticleSpawner(self.rect.center, 10, damage_particles))
                self.hp -= 1
                self.current_damage_delay = self.damage_delay

                # Only take damage from the closest enemy
                closest_enemy = min(enemies, key=lambda sprite:
                                    euclidean_distance(self.rect.center, sprite.rect.center))
                if isinstance(closest_enemy, BaseEnemy):
                    knockback_vector = closest_enemy.x_y
                    self.x_y += knockback_vector * 3
                elif isinstance(closest_enemy, EnemyBullet):
                    closest_enemy.kill()
                
                if self.hp == 0:
                    self.kill()
                else:
                    print(self.hp)

        # Move with wall collision
        self.move_respecting_walls(self.x_y, all_sprites)

        # Shoot bullets
        self.current_attack_delay -= 1
        arrow_keys_pressed = [key for key in ARROW_TO_DIR if keys_pressed[key]]
        # Currently only fire if only one arrow key is being pressed
        if self.current_attack_delay <= 0 and len(arrow_keys_pressed) == 1: 
            self.current_attack_delay = self.attack_delay
            bullet_dir = ARROW_TO_DIR[arrow_keys_pressed[0]]
            bullet = Bullet(bullet_dir, center=self.rect.center)
            self.bullets.add(bullet)

        # Animation
        elif x > 0:
            self.flip = False
            if self.current_damage_delay >= 0:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'damaged_walking')
            else:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'walking')
        elif abs(y) > 0:
            if self.current_damage_delay >= 0:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'damaged_walking')
            else:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'walking')
        elif x < 0:
            self.flip = True
            if self.current_damage_delay >= 0:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'damaged_walking')
            else:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'walking')
        else: 
            if self.current_damage_delay >= 0:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'damaged_idle')
            else:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'idle')

        self.update_animation()
        all_sprites.add(self.particles)


class Bullet(BaseSprite):
    def __init__(self, direction, center=(0, 0)):
        super().__init__(image_assets='assets/bullet.png', center=center)
        self.dir = direction

    def update(self, all_sprites, player, game_map):
        self.particles.add(ParticleSpawner(self.rect.center, 1, bullet_particles))

        self.rect.move_ip(self.dir * BULLET_MOVE_SPEED)

        # Erase the bullet if it hits a wall or goes offscreen
        walls = [sprite for sprite in all_sprites if isinstance(sprite, Wall)]
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
            return
        if not self.rect.colliderect(WINDOW_RECT):
            self.kill()
            return

        all_sprites.add(self.particles)
