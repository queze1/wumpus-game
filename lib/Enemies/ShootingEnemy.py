import pygame

from lib.Enemies import BaseEnemy, EnemyBullet, line_of_sight, get_blocking_walls


class ShootingEnemy(BaseEnemy):
    DIFFICULTY = 3  # How much this enemy is worth in spawning

    ATTACK_DELAY = 90
    ENTERED_LOS_ATTACK_DELAY = 30  # If the player enters LOS, how long to wait before shooting
    ATTACK_STUN = 45  # How long to stop after attacking
    MAX_HP = 3

    SPEED = 3
    BULLET_SPEED = 7

    IMAGE_PATH = 'assets/family_friendly_enemy.png'

    def __init__(self, center=(0, 0)):
        super().__init__(image_assets=self.IMAGE_PATH, center=center)
        self.current_attack_delay = self.ATTACK_DELAY
        self.current_attack_stun = 0

        self.hp = self.MAX_HP
        self.bullets = pygame.sprite.Group()

    def update(self, all_sprites, player, game_map):
        # Handle taking damage
        self.hp = self.handle_damage(player, self.hp)
        if not self.hp:
            all_sprites.remove(self.bullets)
            self.bullets.empty()
            return

        # Handle knockback
        self.handle_knockback(all_sprites)

        # If not stunned, pathfind towards the player
        if self.current_attack_stun <= 0:
            path = self.lazy_theta_star(player.rect.center, all_sprites)
            self.move_along_path(path, self.SPEED, all_sprites)

        # Tick down attack delay and attack stun
        self.current_attack_delay -= 1
        self.current_attack_stun -= 1

        # Check if bullet can reach the player without hitting a wall
        in_los = line_of_sight(self.rect.center, player.rect.center, get_blocking_walls(all_sprites))

        # Check if in LOS
        if in_los and self.rect.center != player.rect.center:
            # Shoot at player if attack delay is over and not on top of enemy
            if (self.current_attack_delay <= 0 and self.current_attack_stun <= 0 and
                    self.rect.center != player.rect.center):
                # Set attack stun and resent attack delay
                self.current_attack_delay = self.ATTACK_DELAY
                self.current_attack_stun = self.ATTACK_STUN

                # Add bullet
                all_sprites.remove(self.bullets)
                self.bullets.add(EnemyBullet(self.rect.center, player.rect.center, self.BULLET_SPEED))
                all_sprites.add(self.bullets)

        # If the enemy is out of LOS, don't tick down the attack delay to much
        elif self.current_attack_delay < self.ENTERED_LOS_ATTACK_DELAY:
            self.current_attack_delay = self.ENTERED_LOS_ATTACK_DELAY
