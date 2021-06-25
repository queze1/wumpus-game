import enum

import pygame

from lib.Enemies import BaseEnemy, get_blocking_walls, line_of_sight
from lib.helpers import euclidean_distance


class STATE(enum.Enum):
    """The states the enemy can be in."""
    SPAWNING_IN = 0
    CHASING = 1
    CHARGING_UP = 2
    CHARGING = 3


class ChargerEnemy(BaseEnemy):
    MAX_HP = 4
    SPEED = 6
    KNOCKBACK_MULTIPLIER = 0.5  # How affected the enemy is by knockback

    CHARGE_MIN_DISTANCE = 80  # How close the enemy has to be to start charging
    CHARGE_UP_TIME = 15  # How many frames to wait while charging up
    CHARGE_SPEED = 28  # Initial charging speed
    CHARGE_MOMENTUM = 0.9  # How much of the charging speed is kept after each frame

    IMAGE_PATH = 'assets/mini_cat.png'

    DIFFICULTY = 3  # How much this enemy is worth in spawning

    def __init__(self, center=(0, 0)):
        super().__init__(image_assets=self.IMAGE_PATH, center=center)
        self.hp = self.MAX_HP

        self.state = STATE.SPAWNING_IN
        self.current_spawning_delay = self.SPAWNING_IN_DELAY

        self.charging_up_timer = 0
        self.charging_vector = None

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

        # Chasing phase
        if self.state == STATE.CHASING:
            path = self.lazy_theta_star(player.rect.center, all_sprites)
            self.move_along_path(path, self.SPEED, all_sprites, self.CHARGE_MIN_DISTANCE)

            # Switch to charging up phase if close enough, in LOS and not directly on top of the player
            blocking_walls = get_blocking_walls(all_sprites, inflate=self.rect.size)
            in_los = line_of_sight(self.rect.center, player.rect.center, blocking_walls)
            close_enough = euclidean_distance(self.rect.center, player.rect.center) <= self.CHARGE_MIN_DISTANCE
            not_on_top = self.rect.center != player.rect.center

            if in_los and close_enough and not_on_top:
                self.state = STATE.CHARGING_UP
                self.charging_up_timer = self.CHARGE_UP_TIME

                # Set the charging vector for the charging phase
                self.charging_vector = (pygame.Vector2(player.rect.center) -
                                        pygame.Vector2(self.rect.center)).normalize() * self.CHARGE_SPEED

        # Charging up phase
        elif self.state == STATE.CHARGING_UP:
            self.charging_up_timer -= 1
            # Start charging when timer is up
            if self.charging_up_timer <= 0:
                self.state = STATE.CHARGING

        # Charging phase - Charge at the player at a high speed, but slow down over time
        elif self.state == STATE.CHARGING:
            self.move_respecting_walls(self.charging_vector, all_sprites)
            self.charging_vector *= self.CHARGE_MOMENTUM

            # Return to chasing phase after charge has stopped
            if self.charging_vector.length() < 1:
                self.state = STATE.CHASING
                self.charging_vector = None
