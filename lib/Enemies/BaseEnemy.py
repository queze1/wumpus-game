import random
from collections import defaultdict
from functools import cache
from itertools import chain
import queue

import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT
from lib.helpers import BaseSprite, euclidean_distance
from lib.Obstacles import Wall


def get_blocking_walls(all_sprites, inflate=(0, 0)):
    """
    Find the walls which can block LOS (not on the edge).
    Optional argument to inflate the walls for pathfinding purposes.
    """
    return [sprite.rect.inflate(inflate) for sprite in all_sprites
            if isinstance(sprite, Wall) and
            0 < (sprite.rect.centerx // 32) < 26 and
            0 < (sprite.rect.centery // 32) < 14]


def line_of_sight(loc, dest_loc, blocking_walls):
    if (not loc) or (not dest_loc):
        return False
    return not any(wall.clipline(loc, dest_loc) for wall in blocking_walls)


def neighbours(loc, dest, blocking_walls):
    # Take the corners of each wall
    important_points = list(chain.from_iterable(
        [(wall.bottomleft, wall.bottomright, wall.topleft, wall.topright) for wall in blocking_walls]
    ))
    important_points.append(dest)

    # Shrink the walls by 1 pixel for pathfinding
    blocking_walls = [wall.inflate(-2, -2) for wall in blocking_walls]

    return [point for point in important_points if line_of_sight(loc, point, blocking_walls) and point != loc]


def theta_star(start_rect, dest, all_sprites):
    """Uses theta* to calculate the optimal path."""

    # Increase the size of the walls to account of the hitbox, the walls are inflated by one more pixel for collision
    blocking_walls = get_blocking_walls(all_sprites, inflate=start_rect.size)

    # Adjust the destination if the destination is unreachable due to it being too close to a wall
    colliding_walls = [wall for wall in blocking_walls if wall.collidepoint(dest)]
    if any(colliding_walls):
        # Find all the walls that are touching this point and combine them
        combined_wall = colliding_walls[0].unionall(colliding_walls)

        # Find the shortest distance to move the destination so that it is no longer too close to a wall
        x, y = dest
        horizontal_line = (0, y, WINDOW_WIDTH, y)
        vertical_line = (x, 0, x, WINDOW_HEIGHT)
        left, right = combined_wall.clipline(horizontal_line)
        top, down = combined_wall.clipline(vertical_line)
        dest = min((top, down, left, right), key=lambda loc: euclidean_distance(loc, dest))

    open_queue = queue.PriorityQueue()
    open_queue.put((0, start_rect.center))
    closed_set = set()

    # g_score[n] is the current cost of the cheapest path from start to n
    g_score = defaultdict(lambda: float('inf'))
    g_score[start_rect.center] = 0
    parents = defaultdict(lambda: None)

    while not open_queue.empty():
        estimated_cost, current = open_queue.get()
        if current == dest:
            # Reconstruct path
            path = []
            while current != start_rect.center:
                path.append(current)
                current = parents[current]
            if start_rect.center == dest:
                path.append(dest)
            return list(reversed(path))

        closed_set.add(current)
        for neighbour in neighbours(current, dest, blocking_walls):
            if neighbour in closed_set:
                continue

            current_parent = parents[current]
            if line_of_sight(current_parent, neighbour, blocking_walls):
                # If there is line of sight between the current point's parent and the neighbour
                # then ignore the current point and use the path from parent to neighbour
                if g_score[current_parent] + euclidean_distance(current_parent, neighbour) < g_score[neighbour]:
                    g_score[neighbour] = g_score[current_parent] + euclidean_distance(current_parent, neighbour)
                    parents[neighbour] = current_parent

                    # g_score[neighbour] + euclidean_distance(neighbour, dest) is a heuristic to estimate the total cost
                    open_queue.put((g_score[neighbour] + euclidean_distance(neighbour, dest), neighbour))

            else:
                # If the length of the path from start to current and from current to neighbour
                # is shorter than the shortest currently known distance from start to neighbour,
                # then update node with the difference.
                if g_score[current] + euclidean_distance(current, neighbour) < g_score[neighbour]:
                    g_score[neighbour] = g_score[current] + euclidean_distance(current, neighbour)
                    parents[neighbour] = current

                    # g_score[neighbour] + euclidean_distance(neighbour, dest) is a heuristic to estimate the total cost
                    open_queue.put((g_score[neighbour] + euclidean_distance(neighbour, dest), neighbour))

    return None


class BaseEnemy(BaseSprite):
    SPAWNING_IN_DELAY = 30  # How long the enemies are immobile when spawning in

    KNOCKBACK_MULTIPLIER = 1
    KNOCKBACK_MOMENTUM = 0.9

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._knockback_vector = pygame.Vector2()
        self._path = None

        self._half_recalculation_delay = 3
        self._current_recalculation_delay = 0

    def lazy_theta_star(self, dest, all_sprites):
        """Calculates the path using theta* but the path is only recalculated roughly every 6 frames."""
        if random.random() > 0.5:
            self._current_recalculation_delay -= 1
        if self._current_recalculation_delay > 0:
            # Adjust the targets
            self._path = self._path[:-1] + [dest]
        else:
            # Recalculate the entire path
            self._path = theta_star(self.rect, dest, all_sprites)
            self._current_recalculation_delay = self._half_recalculation_delay

        return self._path

    def move_along_path(self, path, distance, all_sprites, min_distance=0):
        """
        Move towards the player, following a path generated by Theta*. This takes into account knockback momentum.
        """

        distance_left = distance
        for loc in path:
            vector = pygame.Vector2(loc) - pygame.Vector2(self.rect.center)

            # Check if enemy is directly on top of player
            if not vector:
                return

            # If the player is in LOS, check for min_distance
            if loc == path[-1]:
                if vector.length() < min_distance:
                    return

                elif vector.length() - distance_left < min_distance:
                    vector = vector.normalize() * (vector.length() - min_distance)
                else:
                    vector = vector.normalize() * distance_left

                self.move_respecting_walls(vector, all_sprites)

            elif vector.length() < distance_left:
                self.move_respecting_walls(vector, all_sprites)
            else:
                vector = vector.normalize() * distance_left
                self.move_respecting_walls(vector, all_sprites)
                break

    def handle_damage(self, player, hp_left):
        """Handles enemies taking damage. Should be called every frame."""
        colliding_bullets = pygame.sprite.spritecollide(self, player.bullets, False)
        for bullet in colliding_bullets:
            if self.hp > 0:
                # Take damage
                hp_left -= 1
                bullet.kill()

                if hp_left == 0:
                    self.kill()
                    return 0

                # Add knockback
                knockback_vector = bullet.dir.normalize() * bullet.KNOCKBACK * self.KNOCKBACK_MULTIPLIER
                self._knockback_vector += knockback_vector

        return hp_left

    def handle_knockback(self, all_sprites):
        self.move_respecting_walls(self._knockback_vector, all_sprites)
        self._knockback_vector *= self.KNOCKBACK_MOMENTUM
        if self._knockback_vector.length() < 1:
            self._knockback_vector = pygame.Vector2()
