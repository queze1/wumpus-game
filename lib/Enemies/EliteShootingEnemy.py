import enum

import pygame

from lib.Enemies import BaseEnemy, EnemyBullet, line_of_sight, get_blocking_walls


class STATE(enum.Enum):
    """The states the enemy can be in."""
    SPAWNING_IN = 0
    CHASING = 1
    STUNNED = 2


class EliteShootingEnemy(BaseEnemy):
    DIFFICULTY = 2  # How much this enemy is worth in spawning

    ATTACK_DELAY = 90
    ENTERED_LOS_ATTACK_DELAY = 30  # If the player enters LOS, how long to wait before shooting
    ATTACK_STUN = 30  # How long to stop after attacking
    MAX_HP = 4

    SPEED = 3
    BULLET_SPEED = 6

    IMAGE_PATH = 'assets/upgraded_shooter.png'

    def __init__(self, center=(0, 0)):
        super().__init__(image_assets=self.IMAGE_PATH, center=center)
        self.state = STATE.SPAWNING_IN
        self.current_spawning_delay = self.SPAWNING_IN_DELAY

        self.current_attack_delay = self.ATTACK_DELAY
        self.current_attack_stun = 0

        self.hp = self.MAX_HP
        self.bullets = pygame.sprite.Group()

    def update(self, all_sprites, player, game_map):
        # While the enemy is spawning in, it is immobile and does not take damage or knockback
        if self.state == STATE.SPAWNING_IN:
            self.current_spawning_delay -= 1
            if self.current_spawning_delay <= 0:
                self.state = STATE.CHASING
            else:
                return

        # Handle taking damage
        self.hp = self.handle_damage(player, self.hp)
        if not self.hp:
            return

        # Handle knockback
        self.handle_knockback(all_sprites)

        # Tick down attack delay
        self.current_attack_delay -= 1
        if self.state == STATE.STUNNED:
            # Tick down attack stun
            self.current_attack_stun -= 1
            if self.current_attack_stun <= 0:
                self.state = STATE.CHASING

        # If chasing the player, pathfind towards the player
        elif self.state == STATE.CHASING:
            path = self.lazy_theta_star(player.rect.center, all_sprites)
            self.move_along_path(path, self.SPEED, all_sprites)

            # Check if bullet can reach the player without hitting a wall
            in_los = line_of_sight(self.rect.center, player.rect.center, get_blocking_walls(all_sprites))

            # Shoot at player if attack delay is over, not on top of player and attack delay is over
            if in_los and self.rect.center != player.rect.center and self.current_attack_delay <= 0:
                # Set attack stun, reset attack delay, reset repeat attack delay and reset attack num
                self.current_attack_delay = self.ATTACK_DELAY
                self.current_attack_stun = self.ATTACK_STUN

                # Create the directions for a volley of three bullets
                direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
                direction = direction.normalize() * self.BULLET_SPEED
                volley_dirs = [direction, direction.rotate(30), direction.rotate(-30)]

                all_sprites.remove(self.bullets)
                for bullet_dir in volley_dirs:
                    self.bullets.add(EnemyBullet(self.rect.center, bullet_dir))
                all_sprites.add(self.bullets)

                self.state = STATE.STUNNED

            # If the enemy is out of LOS, don't tick down the attack delay to zero
            elif self.current_attack_delay < self.ENTERED_LOS_ATTACK_DELAY and not in_los:
                self.current_attack_delay = self.ENTERED_LOS_ATTACK_DELAY
