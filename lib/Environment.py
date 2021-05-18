"""This module provides access to the unique behaviours and aspects of each room, as provided in the GameMap."""

from pathlib import Path

import pygame

from lib.Obstacles import Wall

#use this class to get what obstacles and enemies need to be shown in each room.        
class Level(pygame.sprite.Group):
    def __init__(self, room):
        super().__init__()
        
        self.level_dictionary = {
            '#' : Wall
        }

        self.read_room_data(room)

    def read_room_data(self, room):
        with open(f'assets/levels/{room}.txt','r') as tile_data:
            row = 0
            col = 0
            for tile in tile_data.read():
                if not tile in [' ', '\n']:
                    self.add(self.level_dictionary[tile]((16 + (32*col),16 + (32*row))))
                    col += 1
                elif tile == ' ':
                    col += 1
                elif tile == '\n':
                    row += 1
                    col = 0
    
    def reset_room(self, room):
        self.empty()
        self.read_room_data(room)
        print(self.sprites)