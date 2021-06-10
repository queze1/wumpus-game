import pygame

from lib.Enemies import BaseEnemy
from lib.helpers import euclidean_distance


class ChaserEnemy(BaseEnemy):
    MAX_HP = 2
    SPEED = 4

    CHARGE_MIN_DISTANCE = 60
    CHARGE_TIME = 30
    CHARGE_SPEED = 30
    CHARGE_MOMENTUM = 0.9

    IMAGE_PATH = 'assets/enemy.png'

    #DIFFICULTY = 4  # How much this enemy is worth in spawning
    DIFFICULTY = 1

    def __init__(self, center=(0, 0)):
        super().__init__(image_assets=self.IMAGE_PATH, center=center)
        self.hp = self.MAX_HP
        self.current_charge_time = self.CHARGE_TIME
        self.charging_up = False
        self.charging

    def update(self, all_sprites, player, game_map):
        # Handle taking damage
        self.hp = self.handle_damage(player, self.hp)
        if not self.hp:
            return

        # Run towards player unless too close or charging up
        if not self.charging_up or self.charging:
            path = self.lazy_theta_star(player.rect.center, all_sprites)
            self.move_along_path(path, self.SPEED, all_sprites, self.CHARGE_DISTANCE)

            # Start charging up if close enough and in LOS
            if euclidean_distance(self.rect.center, player.rect.center) <= self.CHARGE_DISTANCE:
                self.charging_up = True
                self.current_charge_time = self.CHARGE_TIME  # Reset charging delay

        elif self.charging_up:
            self.current_charge_time -= 1
            if self.current_charge_time == 0:
                self.x_y = (pygame.Vector2(player.rect.center) -
                            pygame.Vector2(self.rect.center)).normalize() * self.CHARGE_SPEED
                self.charging_up = False

