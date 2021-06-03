import pygame
from pygame.transform import scale

from lib.helpers import BaseSprite


class Minimap(BaseSprite):
    def __init__(self, game_map, center=(0, 0)):
        super().__init__(image_assets='assets/minimap/background.png', center=center, alpha=True)
        self.image_base = pygame.image.load('assets/minimap/background.png')
        highest_xy = max([location[0] for location in game_map.rooms.keys()] + 
                         [location[1] for location in game_map.rooms.keys()])
        lowest_xy = min([location[0] for location in game_map.rooms.keys()] + 
                        [location[1] for location in game_map.rooms.keys()])
        self.layout_size = highest_xy - lowest_xy  # how wide/tall will it be
                            
        self.room_size = int((self.rect.width - 40) / self.layout_size)
        
        self.room_types = {'normal': scale(pygame.image.load('assets/minimap/miniroom.png'),
                                           (self.room_size, self.room_size)),
                           'player': scale(pygame.image.load('assets/minimap/playerroom.png'),
                                           (self.room_size, self.room_size)),
                           'cleared': scale(pygame.image.load('assets/minimap/clearedroom.png'),
                                            (self.room_size, self.room_size))}

    def render_minimap(self, game_map):
        locations = [location for location in game_map.rooms.keys()]
        player_location = game_map.player_location
        increment = 0
        while min([location[0] for location in locations] + [location[1] for location in locations]) < 0:
            locations = [(location[0] + 1, location[1] + 1) for location in locations]
            player_location = (player_location[0] + 1, player_location[1] + 1)
            increment += 1

        for location in locations:
            x, y = location
            blit_loc = ((x * self.room_size) + 20, (y * self.room_size) + 20)

            if location == player_location:
                self.render_room(self.room_types['player'], blit_loc)
            elif game_map.rooms[tuple([value - increment for value in location])][-2]:
                self.render_room(self.room_types['cleared'], blit_loc)
            else:
                self.render_room(self.room_types['normal'], blit_loc)

    def render_room(self, room, location):
        x, y = location
        half_room_width = room.get_rect().width/2
        self.image.blit(room, (x - half_room_width, y-half_room_width))

class Healthbar(BaseSprite):
    def __init__(self, player, center=(0,0)):
        super().__init__(image_assets='assets/healthbar/background.png', center=center, alpha=True)
        self.image.set_colorkey((1, 1, 1))
        self.base_image = pygame.image.load('assets/healthbar/background.png')
        self.heart_image = pygame.image.load('assets/healthbar/filled.png')
        self.maintained_hp = player.hp
        self.render_hearts()

    def update(self, all_sprites, player, game_map):
        if self.maintained_hp != player.hp:
            self.maintained_hp = player.hp
            self.render_hearts()

    def render_hearts(self):
        self.image.blit(self.base_image, (0,0))
        print(self.maintained_hp)
        for x in range(0,self.maintained_hp):
            self.image.blit(self.heart_image, (x * 64, 0))
