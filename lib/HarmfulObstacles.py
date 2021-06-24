from lib.helpers import BaseSprite

class Lava(BaseSprite):
    def __init__(self, center=(0, 0)):
        super().__init__(image_assets='assets/lava.png', center=center)

    def update(self, all_sprites, player, game_map):
        if self.rect.colliderect(player.colliding_rect):
        	player.handle_damage(all_sprites, deal_damage=True)