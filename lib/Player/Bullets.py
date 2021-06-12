import pygame

from lib.helpers import BaseSprite, WINDOW_RECT
from lib.Particles import ParticleSpawner
from lib.Obstacles import Wall


bullet_particles = {
    'velocity': ((-1, 1), (-1, 1)),
    'radius': (3, 5),
    'colour': (255, 236, 214),
    'decay': 0.4
}


class Bullet(BaseSprite):
    KNOCKBACK = 5

    def __init__(self, direction, speed, center=(0, 0)):
        super().__init__(image_assets='assets/bullet.png', center=center)
        self.dir = direction * speed

    def update(self, all_sprites, player, game_map):
        self.particles.add(ParticleSpawner(self.rect.center, 1, bullet_particles))

        self.rect.move_ip(self.dir)

        # Erase the bullet if it hits a wall or goes offscreen
        walls = [sprite for sprite in all_sprites if isinstance(sprite, Wall)]
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
            return
        if not self.rect.colliderect(WINDOW_RECT):
            self.kill()
            return

        all_sprites.add(self.particles)
