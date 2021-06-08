from lib.Enemies import BaseEnemy


# TODO: Enemy chases the player, then when it gets close enough, telegraphs a charge for a second then charges

class ChaserEnemy(BaseEnemy):
    MAX_HP = 2
    SPEED = 4
    IMAGE_PATH = 'assets/enemy.png'

    #DIFFICULTY = 4  # How much this enemy is worth in spawning
    DIFFICULTY = 1

    def __init__(self, center=(0, 0)):
        super().__init__(image_assets=self.IMAGE_PATH, center=center)
        self.hp = self.MAX_HP

    def update(self, all_sprites, player, game_map):
        # Handle taking damage
        self.hp = self.handle_damage(player, self.hp)
        if not self.hp:
            return

        # Run towards player unless too close
        path = self.lazy_theta_star(player.rect.center, all_sprites)
        self.move_along_path(path, self.SPEED, all_sprites)
