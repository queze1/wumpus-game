from itertools import chain
import queue

import pygame

from lib.Player import Bullet
from lib.helpers import BaseSprite
from lib.Obstacles import Wall


TEST_ENEMY_SPEED = 3
BOSS_SPEED = 4


def a_star_heuristic(loc, dest_loc):
    # Cartesian distance
    return (pygame.Vector2(dest_loc) - pygame.Vector2(loc)).length()


def is_in_los(loc, dest_loc, blocking_walls):
    return not any(wall.clipline(loc, dest_loc) for wall in blocking_walls)


def find_neighbours(loc, blocking_walls, dest):
    important_points = set(chain.from_iterable(
        [(wall.bottomleft, wall.bottomright, wall.topleft, wall.topright) for wall in blocking_walls]
    ))
    important_points.add(dest)
    neighbours = [(point, a_star_heuristic(loc, point)) for point in important_points
                  if is_in_los(loc, point, blocking_walls)]
    return neighbours


def a_star(start_rect, dest, all_sprites):
    # Increase the size of the walls to account of the hitbox
    blocking_walls = [sprite.rect.inflate(start_rect.width, start_rect.width) for sprite in all_sprites
                      if isinstance(sprite, Wall) and
                      0 < (sprite.rect.centerx // 32) < 26 and
                      0 < (sprite.rect.centery // 32) < 14]

    open_queue = queue.PriorityQueue()
    open_queue.put((0, start_rect.center))
    closed_set = set()

    # For node n, g_score[n] is the cost of the cheapest path from start to n currently known.
    g_score = {start_rect.center: 0}
    came_from = {}

    while not open_queue.empty():
        priority, current = open_queue.get()
        if current == dest:
            # Reconstruct path in reverse order
            path = []
            while current != start_rect.center:
                path.append(current)
                current = came_from[current]
            return list(reversed(path))

        closed_set.add(current)
        for neighbour, cost in find_neighbours(current, blocking_walls, dest):
            if neighbour in closed_set:
                continue
            tentative_g_score = g_score[current] + cost
            if tentative_g_score < g_score.get(neighbour, float('inf')):
                g_score[neighbour] = tentative_g_score
                came_from[neighbour] = current
                open_queue.put((a_star_heuristic(neighbour, dest), neighbour))

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

    def update(self, all_sprites, player):
        self.hp = self.handle_damage(all_sprites, self.hp)
        if not self.hp:
            all_sprites.remove(self.dots)
            self.dots.empty()
            return

        path = a_star(self.rect, player.rect.center, all_sprites)

        all_sprites.remove(self.dots)
        self.dots.empty()
        for center in path:
            self.dots.add(TestDot(center))
        all_sprites.add(self.dots)

        enemy_vector = pygame.Vector2(self.rect.center)
        path_vector = pygame.Vector2(path[0])
        x, y = (path_vector - enemy_vector).normalize() * TEST_ENEMY_SPEED
        self.move_respecting_walls(x, y, all_sprites)


class TestBoss(BaseEnemy):
    def __init__(self, center=(0, 0)):
        super().__init__(image_assets='assets/cat.png', center=center)
        self.hp = 10

    def update(self, all_sprites, player):
        self.hp = self.handle_damage(all_sprites, self.hp)

        enemy_vector = pygame.Vector2(self.rect.center)
        player_vector = pygame.Vector2(player.rect.center)
        if enemy_vector == player_vector:
            return

        x, y = (player_vector - enemy_vector).normalize() * TEST_ENEMY_SPEED
        self.move_respecting_walls(x, y, all_sprites)
