import enum

import pygame

from lib.Enemies import BaseEnemy, EnemyBullet, line_of_sight, get_blocking_walls


class STATE(enum.Enum):
    """The states the enemy can be in."""
    SPAWNING_IN = 0
    RADIAL_BULLET_ATTACK = 1
    HOMING_ATTACKS = 2


class BossEnemy(BaseEnemy):
    DIFFICULTY = 99  # How much this enemy is worth in spawning
    KNOCKBACK_MULTIPLIER = 0  # The boss doesn't take knockback
    MAX_HP = 15

    SPAWNING_IN_DELAY = 60

    RADIAL_ATTACK_DELAY = 10
    ROTATION_SPEED = 5

    SPEED = 4
    BULLET_SPEED = 6

    IMAGE_PATH = 'assets/cat.png'

    def __init__(self, center=(0, 0)):
        super().__init__(image_assets=self.IMAGE_PATH, center=center)
        self.hp = self.MAX_HP
        self.bullets = pygame.sprite.Group()

        self.timer = 0
        self.rotation = 0
        self.state = STATE.SPAWNING_IN
        self.current_spawning_delay = self.SPAWNING_IN_DELAY

    def update(self, all_sprites, player, game_map):
        # While the enemy is spawning in, it is immobile and does not take damage or knockback
        if self.state == STATE.SPAWNING_IN:
            self.current_spawning_delay -= 1
            if self.current_spawning_delay <= 0:
                self.state = STATE.RADIAL_BULLET_ATTACK
            else:
                return

        # Handle taking damage
        self.hp = self.handle_damage(player, self.hp)
        if not self.hp:
            return

        # Handle knockback
        self.handle_knockback(all_sprites)

        self.timer += 1
        if self.state == STATE.RADIAL_BULLET_ATTACK:
            if self.timer >= self.RADIAL_ATTACK_DELAY:
                # Shoot radial bullet pattern
                bullet_dirs = [pygame.Vector2(self.BULLET_SPEED, 0), pygame.Vector2(-self.BULLET_SPEED, 0)]
                bullet_dirs = [bullet_dir.rotate(self.rotation) for bullet_dir in bullet_dirs]
                all_sprites.remove(self.bullets)
                self.bullets.add([EnemyBullet(self.rect.center, bullet_dir) for bullet_dir in bullet_dirs])
                all_sprites.add(self.bullets)

                # Rotate
                self.rotation += 20
                self.timer = 0
