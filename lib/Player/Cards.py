import pygame

from lib.helpers import Direction
from lib.Player.Bullets import Bullet


class BaseAttack:
    DAMAGE = 1
    BULLET_SPEED = 20

    def __init__(self):
        self.damage = self.DAMAGE 
        self.bullet_speed = self.BULLET_SPEED
        self.bullets = pygame.sprite.Group()
        self.icon = pygame.image.load('assets/cards/base_attack.png')
        self.bullet = 'assets/bullets/bullet.png'

        self.particle = {
            'velocity': ((-1, 1), (-1, 1)),
            'radius': (3, 5),
            'colour': (255, 236, 214),
            'decay': 0.4
        }

    def cast(self, entity, direction):
        center = entity.rect.center
        self.bullets.add(Bullet(direction, self.bullet_speed,  self.particle, self.bullet, center=center))
        entity.bullets.add(self.bullets)


class HeavyAttack:
    DAMAGE = 2
    BULLET_SPEED = 30

    def __init__(self):
        self.damage = self.DAMAGE 
        self.bullet_speed = self.BULLET_SPEED
        self.bullets = pygame.sprite.Group()
        self.icon = pygame.image.load('assets/cards/heavy_attack.png')
        self.bullet =  'assets/bullets/heavy_bullet.png'

        self.particle = {
            'velocity': ((-1, 1), (-1, 1)),
            'radius': (2, 4),
            'colour': (0, 255, 0),
            'decay': 0.4
        }

    def cast(self, entity, direction):
        center = entity.rect.center

        if direction in [Direction.RIGHT, Direction.LEFT]:
            self.shoot_bullet(direction, (center[0], center[1] - 10))
            self.shoot_bullet(direction, (center[0], center[1]))
            self.shoot_bullet(direction, (center[0], center[1] + 10))
            self.shoot_bullet(direction, (center[0], center[1] - 20))
            self.shoot_bullet(direction, (center[0], center[1] + 20))
        else:
            self.shoot_bullet(direction, (center[0] + 10, center[1]))
            self.shoot_bullet(direction, (center[0], center[1]))
            self.shoot_bullet(direction, (center[0] - 10, center[1]))
            self.shoot_bullet(direction, (center[0] + 20, center[1]))
            self.shoot_bullet(direction, (center[0] - 20, center[1]))

        entity.bullets.add(self.bullets)

    def shoot_bullet(self, direction, center):
        self.bullets.add(Bullet(direction, self.bullet_speed,  self.particle, self.bullet, center=center))


class Dash:
    DAMAGE = 1
    BULLET_SPEED = 40

    def __init__(self):
        self.icon = pygame.image.load('assets/cards/dash.png')

        self.damage = self.DAMAGE 
        self.bullet_speed = self.BULLET_SPEED
        self.bullets = pygame.sprite.Group()
        self.icon = pygame.image.load('assets/cards/dash_attack.png')
        self.bullet =  'assets/bullets/dash_bullet.png'

        self.particle = {
            'velocity': ((-1, 1), (-1, 1)),
            'radius': (2, 4),
            'colour': (255, 0, 255),
            'decay': 0.4
        }

    def cast(self, entity, direction):
        center = entity.rect.center
        entity.x_y -= direction * 20

        if direction in [Direction.RIGHT, Direction.LEFT]:
            self.shoot_bullet(direction, (center[0], center[1]))
            self.shoot_bullet(direction, (center[0] - 20, center[1]))
            self.shoot_bullet(direction, (center[0] + 20, center[1]))
        else:
            self.shoot_bullet(direction, (center[0], center[1]))
            self.shoot_bullet(direction, (center[0], center[1] - 20))
            self.shoot_bullet(direction, (center[0], center[1] + 20))
        entity.bullets.add(self.bullets)

    def shoot_bullet(self, direction, center):
        self.bullets.add(Bullet(direction, self.bullet_speed,  self.particle, self.bullet, center=center))
