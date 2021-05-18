"""This module provides access to the map of the game."""

from config import WINDOW_HEIGHT, WINDOW_WIDTH
from lib.helpers import Direction
from lib.Obstacles import Wall

class GameMap():
    def __init__(self):
        #the values in self.map refer to level txt files in asset/levels
        self.map = [['0','1','2'],
                    ['3','test_room','5'],
                    ['6','test_room1','8']]
        self.player_location = (1,1) #(x,y)

    def get_room(self):
        x, y = self.player_location
        return self.map[y][x]
    
    def check_player_exited(self, rect):
        if rect.x > WINDOW_WIDTH:
            return Direction.RIGHT
        elif rect.x < 0 - rect.width:
            return Direction.LEFT
        elif rect.y > WINDOW_HEIGHT:
            return Direction.DOWN
        elif rect.y < 0 - rect.height:
            return Direction.UP
        return None

    def move_player(self, direction):
        new_x = self.player_location[0] + direction[0]
        new_y = self.player_location[1] + direction[1]

        try:
            assert new_x >= 0
            assert new_y >= 0
            self.map[new_y][new_x]
            self.player_location = (new_x, new_y)
        except (IndexError, AssertionError):
            pass

        print(self.player_location)
        
    