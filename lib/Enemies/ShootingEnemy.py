import enum

import pygame

from lib.Enemies import BaseEnemy, EnemyBullet, line_of_sight, get_blocking_walls


class STATE(enum.Enum):
    """The states the enemy can be in."""
    SPAWNING_IN = 0
    CHASING = 1
    STUNNED = 2
    SHOOTING = 3


class ShootingEnemy(BaseEnemy):
    DIFFICULTY = 1  # How much this enemy is worth in spawning

    ATTACK_DELAY = 90
    ENTERED_LOS_ATTACK_DELAY = 30  # If the player enters LOS, how long to wait before shooting
    ATTACK_STUN = 30  # How long to stop after attacking
    MAX_HP = 2

    SPEED = 3
    BULLET_SPEED = 7

    BULLET_NUM = 2
    REPEAT_ATTACK_DELAY = 7

    IMAGE_PATH = 'assets/basic_shooter.png'

    def __init__(self, center=(0, 0)):
        super().__init__(image_assets=self.IMAGE_PATH, center=center)
        self.state = STATE.SPAWNING_IN
        self.current_spawning_delay = self.SPAWNING_IN_DELAY

        self.current_attack_delay = self.ATTACK_DELAY
        self.current_attack_stun = 0

        self.current_bullet_dir = pygame.Vector2()  # Direction for the volley of bullets
        self.current_bullet_num = 0
        self.current_repeat_delay = 0

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

        elif self.state == STATE.SHOOTING:
            # Tick down repeat attack delay
            self.current_repeat_delay -= 1
            if self.current_repeat_delay <= 0:
                # Reset repeat attack delay
                self.current_repeat_delay = self.REPEAT_ATTACK_DELAY

                # Fire a bullet in a fixed direction
                all_sprites.remove(self.bullets)
                self.bullets.add(EnemyBullet(self.rect.center, self.current_bullet_dir))
                all_sprites.add(self.bullets)

                self.current_bullet_num += 1
                # If enough bullets have been shot, switch to stunned state
                if self.current_bullet_num == self.BULLET_NUM:
                    self.state = STATE.STUNNED

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
                self.current_repeat_delay = 0
                self.current_bullet_num = 0

                # Set the direction of the bullet volley and set the state to shooting
                self.current_bullet_dir = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
                self.current_bullet_dir = self.current_bullet_dir.normalize() * self.BULLET_SPEED
                self.state = STATE.SHOOTING

            # If the enemy is out of LOS, don't tick down the attack delay to zero
            elif self.current_attack_delay < self.ENTERED_LOS_ATTACK_DELAY and not in_los:
                self.current_attack_delay = self.ENTERED_LOS_ATTACK_DELAY
