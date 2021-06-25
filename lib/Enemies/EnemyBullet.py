import pygame

from lib.helpers import BaseSprite
from lib.Obstacles import Wall


class EnemyBullet(BaseSprite):
    def __init__(self, center, direction):
        super().__init__(image_assets='assets/enemy_bullet.png', center=center)
        self.direction = direction

    def update(self, all_sprites, player, gamemap):
        walls = [sprite for sprite in all_sprites if isinstance(sprite, Wall)]
        self.rect.move_ip(self.direction)
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
