from collections import defaultdict
from itertools import chain
import queue

import pygame

from lib.Player import Bullet
from lib.helpers import BaseSprite, Direction
from lib.Obstacles import Wall


TEST_ENEMY_SPEED = 3
BOSS_SPEED = 4

# pathfinding testing
ARROW_TO_DIR = {pygame.K_UP: Direction.UP,
                pygame.K_LEFT: Direction.LEFT,
                pygame.K_DOWN: Direction.DOWN,
                pygame.K_RIGHT: Direction.RIGHT}


def euclidean_distance(loc, dest_loc):
    return (pygame.Vector2(dest_loc) - pygame.Vector2(loc)).length()


def line_of_sight(loc, dest_loc, blocking_walls):
    if (not loc) or (not dest_loc):
        return False
    return not any(wall.clipline(loc, dest_loc) for wall in blocking_walls)


def neighbours(loc, dest, blocking_walls):
    # Inflate the walls by one pixel to make sure that LOS detection works property
    inflated_walls = [wall.inflate(2, 2) for wall in blocking_walls]
    important_points = list(chain.from_iterable(
        [(wall.bottomleft, wall.bottomright, wall.topleft, wall.topright) for wall in inflated_walls]
    ))
    important_points.append(dest)
    return [point for point in important_points if line_of_sight(loc, point, blocking_walls) and point != loc]


def theta_star(start_rect, dest, all_sprites):
    # Increase the size of the walls to account of the hitbox
    blocking_walls = [sprite.rect.inflate(start_rect.width, start_rect.width) for sprite in all_sprites
                      if isinstance(sprite, Wall) and
                      0 < (sprite.rect.centerx // 32) < 26 and
                      0 < (sprite.rect.centery // 32) < 14]

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
    hp = None

    def handle_damage(self, all_sprites, hp_left):
        bullets = [sprite for sprite in all_sprites if isinstance(sprite, Bullet)]
        colliding_bullets = pygame.sprite.spritecollide(self, bullets, False)
        for bullet in colliding_bullets:
            if self.hp > 0:
                hp_left -= 1
                bullet.kill()
                if hp_left == 0:
                    self.kill()
                    return 0
        return hp_left


class TestDot(BaseSprite):
    def __init__(self, center=(0, 0)):
        super().__init__(image_assets='assets/bullet.png', center=center)


class TestEnemy(BaseEnemy):
    def __init__(self, center=(0, 0)):
        super().__init__(image_assets='assets/enemy.png', center=center)
        self.hp = 1
        self.dots = pygame.sprite.Group()

    def update(self, all_sprites, player, game_map):
        self.hp = self.handle_damage(all_sprites, self.hp)
        if not self.hp:
            all_sprites.remove(self.dots)
            self.dots.empty()
            return

        # TODO: make paths have inertia
        path = theta_star(self.rect, player.rect.center, all_sprites)
        if path:
            all_sprites.remove(self.dots)
            self.dots.empty()
            for center in path:
                self.dots.add(TestDot(center))
            all_sprites.add(self.dots)

            vector = pygame.Vector2(path[0]) - pygame.Vector2(self.rect.center)
            x, y = vector.normalize() * TEST_ENEMY_SPEED
            self.move_respecting_walls(x, y, all_sprites)


class TestBoss(BaseEnemy):
    def __init__(self, center=(0, 0)):
        super().__init__(image_assets='assets/cat.png', center=center)
        self.hp = 10
        self.dots = pygame.sprite.Group()

    def update(self, all_sprites, player, game_map):
        self.hp = self.handle_damage(all_sprites, self.hp)

        path = theta_star(self.rect, player.rect.center, all_sprites)
        if path:
            all_sprites.remove(self.dots)
            self.dots.empty()
            for center in path:
                self.dots.add(TestDot(center))
            all_sprites.add(self.dots)

            vector = pygame.Vector2(path[0]) - pygame.Vector2(self.rect.center)
            x, y = vector.normalize() * TEST_ENEMY_SPEED
            self.move_respecting_walls(x, y, all_sprites)