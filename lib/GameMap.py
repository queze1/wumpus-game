"""
This module provides access to the game map, which generates the dungeon,
places environmental objects and places enemies.
"""

from itertools import chain
import os
import random

import pygame

from config import WINDOW_HEIGHT, WINDOW_WIDTH
from lib.helpers import Direction
from lib.Obstacles import Wall


LEVEL_PATH = 'assets/levels'
NORMAL_LEVEL_PATHS = [f'{LEVEL_PATH}/{name}' for name in os.listdir(LEVEL_PATH) if name.startswith('normal')]
STARTING_LEVEL_PATH = f'{LEVEL_PATH}/starting_room.txt'
LEVEL_DICTIONARY = {
    '#': Wall
}

# What coordinates will be kept open to create an exit for each direction
DIR_TO_EXIT_COORDS = {Direction.UP: ((12, 0), (13, 0), (14, 0)),
                      Direction.DOWN: ((12, 14), (13, 14), (14, 14)),
                      Direction.LEFT: ((0, 6), (0, 7), (0, 8)),
                      Direction.RIGHT: ((26, 6), (26, 7), (26, 8))}


def room_neighbours(room_tuple, exclude=()):
    """Find the room tuples that are next to this one, excluding certain rooms."""
    x, y = room_tuple
    # Order is up, down, left, right
    return [room for room in [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
            if room not in exclude]


def load_room(room_path, exit_directions):
    # Find all the coordinates that need to be kept open for exits
    exit_coords = list(chain.from_iterable([DIR_TO_EXIT_COORDS[direction] for direction in exit_directions]))

    room_sprites = pygame.sprite.Group()
    with open(room_path, 'r') as tile_data:
        for y, line in enumerate(tile_data.readlines()):
            for x, char in enumerate(line):
                if not (char in [' ', '\n']):
                    if (x, y) not in exit_coords:
                        room_sprites.add(LEVEL_DICTIONARY[char]((16 + (32 * x), 16 + (32 * y))))

    return room_sprites


class GameMap:
    def __init__(self, num_rooms):
        starting_room = (0, 0)
        room_locs = [starting_room]
        self.player_location = starting_room
        self.environmental_sprites = pygame.sprite.Group()

        # Generate dungeon
        while True:
            for room in room_locs:
                if len(room_locs) == num_rooms:
                    break

                # Iterate through all the room's neighbours, excluding any already occupied rooms
                for neighbour in room_neighbours(room, exclude=room_locs):
                    neighbour_free_spaces = room_neighbours(neighbour, room_locs)
                    # If the neighbour cell would already be next to 3 rooms or more, give up
                    if len(neighbour_free_spaces) <= 1:
                        continue

                    # 50% chance of placing room
                    if random.random() > 0.5:
                        room_locs.append(neighbour)

            if len(room_locs) == num_rooms:
                break

        # TODO: Place a boss room at the last end room
        # Load a room for each room location
        self.rooms = {}
        for room_loc in room_locs:
            # Find the directions in which exits should be located
            exit_directions = []
            # Order of room_neighbour is up, down, left, right
            for neighbour, direction in zip(room_neighbours(room_loc), Direction.UP_DOWN_LEFT_RIGHT):
                if neighbour in room_locs:
                    exit_directions.append(direction)

            if room_loc == starting_room:
                self.rooms[room_loc] = load_room(STARTING_LEVEL_PATH, exit_directions)
            else:
                self.rooms[room_loc] = load_room(random.choice(NORMAL_LEVEL_PATHS), exit_directions)

        # Load starting room
        self.environmental_sprites = self.rooms[starting_room]
        print(room_locs)

    @staticmethod
    def check_exited(rect):
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
        x, y = self.player_location
        self.player_location = (x + direction[0], y + direction[1])

    def change_room(self, room_loc=None):
        if not room_loc:
            room_loc = self.player_location

        self.environmental_sprites = self.rooms[room_loc]
