from config import WINDOW_HEIGHT, WINDOW_WIDTH

class Direction():
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameMap():
    def __init__(self):
        self.map = [[0,1,2],
                    [3,4,5],
                    [6,7,8]]
        self.player_location = (1,1) #(x,y)
        self.player_room = self.map[self.player_location[1]][self.player_location[0]]

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
            self.player_room = self.map[new_y][new_x]
            self.player_location = (new_x, new_y)
        except (IndexError, AssertionError):
            pass

        print(self.player_location, self.player_room)
        