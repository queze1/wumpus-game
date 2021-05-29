import pygame

from lib.Player import Bullet
from lib.helpers import BaseSprite
from lib.Obstacles import Wall


TEST_ENEMY_SPEED = 3
BOSS_SPEED = 4


class BaseEnemy(BaseSprite):
    def handle_damage(self, all_sprites, hp_left):
        bullets = [sprite for sprite in all_sprites if isinstance(sprite, Bullet)]
        colliding_bullets = pygame.sprite.spritecollide(self, bullets, False)
        for bullet in colliding_bullets:
            if self.hp > 0:
                hp_left -= 1
                bullet.kill()
                if hp_left == 0:
                    self.kill()
                    return 0
        return hp_left


class TestEnemy(BaseEnemy):
    def __init__(self, center=(0, 0)):
        super().__init__(image_path='assets/enemy.png', center=center)
        self.hp = 1

    def update(self, all_sprites, player):
        self.hp = self.handle_damage(all_sprites, self.hp)
        if not self.hp:
            return

        enemy_vector = pygame.Vector2(self.rect.center)
        player_vector = pygame.Vector2(player.rect.center)
        if enemy_vector == player_vector:
            return

        x, y = (player_vector - enemy_vector).normalize() * TEST_ENEMY_SPEED
        self.move_respecting_walls(x, y, all_sprites)


class TestBoss(BaseEnemy):
    def __init__(self, center=(0, 0)):
        super().__init__(image_path='assets/cat.png', center=center)
        self.hp = 10

    def update(self, all_sprites, player):
        self.hp = self.handle_damage(all_sprites, self.hp)

        enemy_vector = pygame.Vector2(self.rect.center)
        player_vector = pygame.Vector2(player.rect.center)
        if enemy_vector == player_vector:
            return

        x, y = (player_vector - enemy_vector).normalize() * TEST_ENEMY_SPEED
        self.move_respecting_walls(x, y, all_sprites)

