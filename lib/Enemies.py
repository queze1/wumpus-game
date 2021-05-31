import queue

import pygame

from lib.Player import Bullet
from lib.helpers import BaseSprite
from lib.Obstacles import Wall


TEST_ENEMY_SPEED = 3
BOSS_SPEED = 4


def a_star_heuristic(loc, dest_loc):
    x, y = loc
    dest_x, dest_y = dest_loc
    return (dest_x - x) ** 2 + (dest_y - y) ** 2


def coord_to_grid(coord):
    x, y = coord
    return x // 32, y // 32


def generate_neighbours(loc):
    x, y = loc
    neighbours = [(x - 1, y, 1), (x + 1, y, 1), (x, y - 1, 1), (x, y + 1, 1)]
    neighbours += [(x - 1, y - 1, 2), (x + 1, y - 1, 2), (x - 1, y + 1, 2), (x + 1, y + 1, 2)]
    return {(x, y): cost for x, y, cost in neighbours if (0 <= x <= 26 and 0 <= y <= 14)}


def grid_a_star(start_coord, dest_coord, all_sprites):
    """
    Initial A* with grid. Returns path from destination to start.
    """
    start = coord_to_grid(start_coord)
    dest = coord_to_grid(dest_coord)
    walls = [sprite.rect.center for sprite in all_sprites if isinstance(sprite, Wall)]

    open_queue = queue.PriorityQueue()
    open_queue.put((0, start))
    closed_set = set(map(coord_to_grid, walls))

    # For node n, g_score[n] is the cost of the cheapest path from start to n currently known.
    g_score = {start: 0}
    came_from = {}

    while not open_queue.empty():
        priority, current = open_queue.get()
        if current == dest:
            # Reconstruct path in reverse order
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            return list(reversed(path))

        closed_set.add(current)
        for neighbour, cost in generate_neighbours(current).items():
            if neighbour in closed_set:
                continue

            tentative_g_score = g_score[current] + cost
            if tentative_g_score < g_score.get(neighbour, float('inf')):
                g_score[neighbour] = tentative_g_score
                came_from[neighbour] = current
                open_queue.put((a_star_heuristic(neighbour, dest), neighbour))

    return None


def a_star(start_coord, dest_coord, all_sprites):
    grid_path = grid_a_star(start_coord, dest_coord, all_sprites)
    return [(x * 32 + 16, y * 32 + 16) for x, y in grid_path]


# TODO: try theta*
# TODO: add inertia to paths so that enemies do not keep on switching paths


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

        all_sprites.remove(self.dots)
        self.dots.empty()
        path = a_star(self.rect.center, player.rect.center, all_sprites)
        for center in path:
            self.dots.add(TestDot(center=center))
        all_sprites.add(self.dots)

        if path:
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
