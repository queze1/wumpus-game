"""
This module provides access to the game map and the enemy generator.

The game map generates the dungeon and places environmental objects when the player changes rooms.
The enemy generator places enemies and pathfinds for the enemies.
"""

from itertools import chain
import os
import random

import pygame

from config import *
from lib import Enemies
from lib.helpers import Direction
from lib.Obstacles import Wall
from lib.Player import Player


LEVEL_PATH = 'assets/levels'
NORMAL_LEVEL_PATHS = [f'{LEVEL_PATH}/{name}' for name in os.listdir(LEVEL_PATH) if name.startswith('normal')]
STARTING_LEVEL_PATH = f'{LEVEL_PATH}/starting_room.txt'
BOSS_LEVEL_PATH = f'{LEVEL_PATH}/boss_room.txt'
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
    # Order is up, left, down, right WASD
    return [room for room in [(x, y - 1), (x - 1, y), (x, y + 1), (x + 1, y)]
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


class EnemySpawner:
    def __init__(self):
        self.lvl_number = 0

        self.is_boss = False
        self.waves_left = 0
        self.room_cleared = True
        self.current_wave_delay = 0
        self.enemies = pygame.sprite.Group()

    def room_setup(self, is_cleared, is_boss=False):
        self.enemies.empty()
        self.is_boss = is_boss
        self.current_wave_delay = 0
        if is_cleared:
            self.waves_left = 0
        else:
            self.lvl_number += 1
            if not is_boss:
                self.waves_left = ROOM_WAVE_NUM
            else:
                self.waves_left = 1

    def spawn_enemies(self, all_sprites):
        """
        Spawns enemies. Before entering a room with enemies, call room_setup().
        Returns True if the room is cleared. Returns False if the room is not cleared.
        """
        if self.waves_left:
            # Spawn the boss
            if self.is_boss:
                self.enemies.add(Enemies.TestBoss((WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)))
                self.waves_left -= 1

            elif any([isinstance(sprite, Enemies.BaseEnemy) for sprite in all_sprites]):
                # Reset wave delay if enemies have spawned
                self.current_wave_delay = WAVE_DELAY

            elif not any([isinstance(sprite, Enemies.BaseEnemy) for sprite in all_sprites]):
                # Handle wave delay
                if self.current_wave_delay:
                    self.current_wave_delay -= 1
                    return False

                # Used for sanity checking spawns
                no_spawn = [sprite.rect.inflate(10, 10) for sprite in all_sprites if isinstance(sprite, Wall)]
                no_spawn.append([sprite.rect.inflate(400, 400) for sprite in all_sprites
                                 if isinstance(sprite, Player)][0])

                # Use points based system for spawning
                enemies = {Enemies.ShootingEnemy: Enemies.ShootingEnemy.DIFFICULTY,
                           Enemies.ChaserEnemy: Enemies.ChaserEnemy.DIFFICULTY}
                enemy_value = int(self.lvl_number ** 1.1 + self.lvl_number/2 + 2)

                current_enemy_value = 0
                while current_enemy_value < enemy_value:
                    chosen_enemy = random.choice(list(enemies))
                    while True:
                        if enemies[chosen_enemy] + current_enemy_value <= enemy_value:
                            break
                        chosen_enemy = random.choice(list(enemies))

                    current_enemy_value += enemies[chosen_enemy]

                    sane = False
                    while not sane:
                        enemy = chosen_enemy((random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)))
                        if enemy.rect.collidelist(no_spawn) == -1:
                            sane = True

                    self.enemies.add(enemy)
                    no_spawn.append(enemy.rect.inflate(20, 20))

                self.waves_left -= 1

            return False

        # If there are no enemies and all waves have been cleared, this room is cleared
        elif not any([isinstance(sprite, Enemies.BaseEnemy) for sprite in all_sprites]):
            return True


class GameMap:
    def __init__(self, num_rooms):
        starting_room = (0, 0)
        room_locs = [starting_room]
        self.boss_room_loc = None
        self.player_location = starting_room
        self.environmental_sprites = pygame.sprite.Group()
        self.temp_walls = pygame.sprite.Group()
        self.enemy_spawner = EnemySpawner()

        # Generate dungeon
        while True:
            for room in room_locs:
                # Iterate through all the room's neighbours, excluding any already occupied rooms
                for neighbour in room_neighbours(room, exclude=room_locs):
                    # If enough rooms have been placed, give up
                    if len(room_locs) == num_rooms:
                        break

                    neighbour_free_spaces = room_neighbours(neighbour, room_locs)
                    # If the neighbour cell would already be next to 3 rooms or more, give up
                    if len(neighbour_free_spaces) <= 1:
                        continue

                    # 50% chance of placing room
                    if random.random() > 0.5:
                        room_locs.append(neighbour)

                if len(room_locs) == num_rooms:
                    break

            if len(room_locs) == num_rooms:
                break

        # Load a room for each room location
        self.rooms = {}
        for room_loc in reversed(room_locs):  # Iterate from the last placed rooms to place the boss room
            # Find the directions in which exits should be located
            exit_directions = []
            # Order of room_neighbour is up, left, down, right WASD
            for neighbour, direction in zip(room_neighbours(room_loc), Direction.UP_LEFT_DOWN_RIGHT):
                if neighbour in room_locs:
                    exit_directions.append(direction)

            if room_loc == starting_room:
                self.rooms[room_loc] = [load_room(STARTING_LEVEL_PATH, exit_directions), True, exit_directions]
            # If the boss room has not been placed yet, and this room is a dead end, make this the boss room
            elif not self.boss_room_loc and (len(exit_directions) == 1):
                self.boss_room_loc = room_loc
                self.rooms[room_loc] = [load_room(BOSS_LEVEL_PATH, exit_directions), False, exit_directions]
            else:
                self.rooms[room_loc] = [load_room(random.choice(NORMAL_LEVEL_PATHS), exit_directions),
                                        False, exit_directions]

        # Load starting room
        self.environmental_sprites, _, _ = self.rooms[starting_room]

    @staticmethod
    def check_exited(rect):
        if rect.x > WINDOW_WIDTH - 10:
            return Direction.RIGHT
        elif rect.x < (0 - rect.width) + 10:
            return Direction.LEFT
        elif rect.y > WINDOW_HEIGHT - 10:
            return Direction.DOWN
        elif rect.y < (0 - rect.height) + 10:
            return Direction.UP
        return None

    def is_cleared(self):
        is_cleared = self.rooms[self.player_location][1]
        return is_cleared

    def set_cleared(self, is_cleared):
        self.rooms[self.player_location][1] = is_cleared

    def lock_room(self, all_sprites):
        # TODO: Make the doors at the exits thinner
        room_exit_dirs = self.rooms[self.player_location][2]

        for direction in room_exit_dirs:
            print(f'door closed at {direction}')
            for x, y in DIR_TO_EXIT_COORDS[direction]:
                self.temp_walls.add(Wall((16 + (32 * x), 16 + (32 * y))))
            all_sprites.add(self.temp_walls)

    def unlock_room(self, all_sprites):
        print('doors unlocked')
        all_sprites.remove(self.temp_walls)
        self.temp_walls.empty()

    def handle_rooms(self, all_sprites, player, minimap):
        dir_exited = self.check_exited(player.rect)

        if not dir_exited:
            return

        # Move player location
        x, y = self.player_location
        x_change, y_change = dir_exited
        self.player_location = (x + x_change, y + y_change)
        print(f'new location: {self.player_location}')

        # Change sprites
        all_sprites.remove(player.bullets)
        player.bullets.empty()
        all_sprites.remove(self.environmental_sprites)
        all_sprites.remove(self.enemy_spawner.enemies)
        self.environmental_sprites, is_cleared, _ = self.rooms[self.player_location]
        all_sprites.add(self.environmental_sprites)

        if not is_cleared:
            # Move the player further into the room so that the player doesn't clip into them
            player.rect.x -= x_change * (WINDOW_WIDTH - 40)
            player.rect.y -= y_change * (WINDOW_HEIGHT - 40)
        else:
            player.rect.x -= x_change * WINDOW_WIDTH
            player.rect.y -= y_change * WINDOW_HEIGHT

        if not is_cleared:
            if self.player_location == self.boss_room_loc:
                self.enemy_spawner.room_setup(is_cleared=False, is_boss=True)
            else:
                self.enemy_spawner.room_setup(is_cleared=False, is_boss=False)
            self.lock_room(all_sprites)
        else:
            self.enemy_spawner.room_setup(is_cleared=True)

        minimap.render_minimap(self, all_sprites)
