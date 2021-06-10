import pygame

from lib.Enemies import BaseEnemy, get_blocking_walls, line_of_sight
from lib.helpers import euclidean_distance


class ChargerEnemy(BaseEnemy):
    MAX_HP = 4
    SPEED = 5

    CHARGE_MIN_DISTANCE = 80
    CHARGE_TIME = 10
    CHARGE_SPEED = 22
    CHARGE_MOMENTUM = 0.9

    IMAGE_PATH = 'assets/enemy.png'

    # DIFFICULTY = 4  # How much this enemy is worth in spawning
    DIFFICULTY = 1

    def __init__(self, center=(0, 0)):
        super().__init__(image_assets=self.IMAGE_PATH, center=center)
        self.hp = self.MAX_HP
        self.current_charge_time = self.CHARGE_TIME
        self.charging_up = False
        self.charging = False
        self.charging_vector = pygame.Vector2()

    def update(self, all_sprites, player, game_map):
        # Handle taking damage
        self.hp = self.handle_damage(player, self.hp)
        if not self.hp:
            return

        # Run towards player unless too close or charging up
        if not (self.charging_up or self.charging):
            path = self.lazy_theta_star(player.rect.center, all_sprites)
            self.move_along_path(path, self.SPEED, all_sprites, self.CHARGE_MIN_DISTANCE)

            # Start charging up if close enough, in LOS and not directly on top of the player
            blocking_walls = get_blocking_walls(all_sprites, inflate=self.rect.size)
            in_los = line_of_sight(self.rect.center, player.rect.center, blocking_walls)
            close_enough = euclidean_distance(self.rect.center, player.rect.center) <= self.CHARGE_MIN_DISTANCE
            not_on_top = self.rect.center != player.rect.center

            if in_los and close_enough and not_on_top:
                self.charging_up = True
                self.current_charge_time = self.CHARGE_TIME  # Reset charging delay

                # Set the charging vector
                self.charging_vector = (pygame.Vector2(player.rect.center) -
                            pygame.Vector2(self.rect.center)).normalize() * self.CHARGE_SPEED

        elif self.charging_up:
            self.current_charge_time -= 1
            # Start charging when the timer is up
            if self.current_charge_time <= 0:
                self.charging_up = False
                self.charging = True

        else:
            # Charge at the player at a high speed, but slow down over time
            self.move_respecting_walls(self.charging_vector, all_sprites)
            self.charging_vector *= self.CHARGE_MOMENTUM
            if self.charging_vector.length() < 1:
                self.charging_vector = pygame.Vector2()
                self.charging = False
