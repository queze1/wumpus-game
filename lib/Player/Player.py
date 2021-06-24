"""This module provides access to several classes that are associated with the player character."""
from random import shuffle
import pygame

from lib.Enemies import BaseEnemy, EnemyBullet
from lib.helpers import BaseSprite, change_action, euclidean_distance, Direction
from lib.Particles import ParticleSpawner
from lib.Player.Bullets import Bullet
from lib.Player.Cards import *


KEY_TO_DIR = {pygame.K_w: Direction.UP,
              pygame.K_a: Direction.LEFT,
              pygame.K_s: Direction.DOWN,
              pygame.K_d: Direction.RIGHT}

ARROW_TO_DIR = {pygame.K_UP: Direction.UP,
                pygame.K_LEFT: Direction.LEFT,
                pygame.K_DOWN: Direction.DOWN,
                pygame.K_RIGHT: Direction.RIGHT}


damage_particles = {
    'velocity': ((-3, 3), (-3, 3)),
    'radius': (2, 3),
    'colour': (255, 236, 214),
    'decay': 0.1
}


class Player(BaseSprite):
    SPEED = 5
    MOMENTUM_COEFFICIENT = 0.66
    KNOCKBACK = 30

    BULLET_SPEED = 20
    ATTACK_DELAY = 20

    STARTING_MAX_HP = 5
    DAMAGE_DELAY = 100  # How long the player receives invulnerability after taking damage

    # All the assets used for animations
    IMAGE_ASSETS = [('idle', 'assets/player/player_idle.png', [40, 40, 40, 40], (12, 32)),
                    ('walking', 'assets/player/player_walking.png', [15, 15, 15, 15, 15], (12, 32)),
                    ('damaged_idle', 'assets/player/player_damaged_idle.png', [7, 7, 7, 7], (12, 32)),
                    ('damaged_walking', 'assets/player/player_damaged_walking.png', [7, 7, 7, 7, 7], (12, 32))]

    def __init__(self, center=(0, 0)):
        super().__init__(image_assets=self.IMAGE_ASSETS, center=center)
        self.hp = self.STARTING_MAX_HP
        self.current_attack_delay = 0
        self.current_damage_delay = 0
        self.x_y = pygame.Vector2()  # Current vector velocity

        self.deck = [BaseAttack()]
        self.discard_pile = []
        self.attack_delay = self.ATTACK_DELAY - (len(self.deck)*3)

        self.bullets = pygame.sprite.Group()

    def handle_damage(self, all_sprites):
        self.current_damage_delay -= 1
        if self.current_damage_delay <= 0:
            # Check if you collided with an enemy or enemy bullet
            enemies = [sprite for sprite in all_sprites if isinstance(sprite, (BaseEnemy, EnemyBullet))]
            enemies_collided = pygame.sprite.spritecollide(self, enemies, False)

            if enemies_collided:
                self.particles.add(ParticleSpawner(self.rect.center, 10, damage_particles))
                self.hp -= 1
                self.current_damage_delay = self.DAMAGE_DELAY

                # Find the closest enemy and only take damage from that one
                enemy = min(enemies, key=lambda sprite: euclidean_distance(self.rect.center, sprite.rect.center))
                if isinstance(enemy, BaseEnemy):
                    knockback_vector = pygame.Vector2(self.rect.center) - pygame.Vector2(enemy.rect.center)
                    if knockback_vector:
                        knockback_vector = knockback_vector.normalize() * self.KNOCKBACK
                    self.x_y += knockback_vector

                elif isinstance(enemy, EnemyBullet):
                    enemy.kill()

                if self.hp == 0:
                    self.kill()
                    return False

        return True

    def update(self, all_sprites, player, game_map):
        # WASD movement
        delta_x_y = pygame.Vector2()
        keys_pressed = pygame.key.get_pressed()
        for key in KEY_TO_DIR:
            if keys_pressed[key]:
                delta_x_y += KEY_TO_DIR[key]
        if delta_x_y:
            delta_x_y = delta_x_y.normalize() * self.SPEED

        # Smooth out the velocity
        self.x_y = self.x_y * self.MOMENTUM_COEFFICIENT + delta_x_y * (1 - self.MOMENTUM_COEFFICIENT)
        if self.x_y.length() < 0.5:
            self.x_y = pygame.Vector2()

        # Handle damage
        if not self.handle_damage(all_sprites):
            return

        # Move with wall collision
        self.move_respecting_walls(self.x_y, all_sprites)

        # Kill all enemies in room
        if keys_pressed[pygame.K_b]:
            for enemy in game_map.enemy_spawner.enemies:
                enemy.kill()
            game_map.enemy_spawner.waves_left = 0

        self.current_attack_delay -= 1
        arrow_keys_pressed = [key for key in ARROW_TO_DIR if keys_pressed[key]]
        # If only one arrow key is pressed and the attack delay is over, shoot
        if not self.deck:
            self.deck = self.discard_pile
            self.discard_pile = []

        if self.current_attack_delay <= 0 and len(arrow_keys_pressed) == 1: 
            self.current_attack_delay = self.ATTACK_DELAY
            bullet_dir = ARROW_TO_DIR[arrow_keys_pressed[0]]
            card = self.deck.pop(0)
            card.cast(self, bullet_dir)
            self.discard_pile.append(card)

        # Animation
        x, y = delta_x_y
        is_damaged = self.current_damage_delay > 0
        if not delta_x_y:
            if is_damaged:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'damaged_idle')
            else:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'idle')
        else:
            if x:
                self.flip = x < 0
            if is_damaged:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'damaged_walking')
            else:
                self.state, self.animation_frame = change_action(self.state, self.animation_frame, 'walking')

        self.update_animation()
        all_sprites.add(self.particles)
