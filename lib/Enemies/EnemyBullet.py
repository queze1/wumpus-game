import pygame

from lib.helpers import BaseSprite
from lib.Obstacles import Wall


class EnemyBullet(BaseSprite):
    def __init__(self, center, target, speed):
        super().__init__(image_assets='assets/enemy_bullet.png', center=center)
        self.direction = (pygame.Vector2(target) - pygame.Vector2(center)).normalize() * speed

    def update(self, all_sprites, player, gamemap):
        x, y = self.direction
        self.rect.move_ip(x, y)

        walls = [sprite for sprite in all_sprites if isinstance(sprite, Wall)]
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
            return
