import random
from collections import defaultdict
from itertools import chain
import queue

import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT
from lib.helpers import BaseSprite, Direction, euclidean_distance
from lib.Obstacles import Wall


TEST_ENEMY_SPEED = 4
SHOOTING_ENEMY_SPEED = 3
ENEMY_BULLET_SPEED = 6
BOSS_SPEED = 4

# pathfinding testing
ARROW_TO_DIR = {pygame.K_UP: Direction.UP,
                pygame.K_LEFT: Direction.LEFT,
                pygame.K_DOWN: Direction.DOWN,
                pygame.K_RIGHT: Direction.RIGHT}


def get_blocking_walls(all_sprites, inflate=(0, 0)):
    """
    Find the walls which can block LOS (not on the edge).
    Optional argument to inflate the walls for pathfinding purposes.
    """

    x, y = inflate
    return [sprite.rect.inflate(x, y) for sprite in all_sprites
            if isinstance(sprite, Wall) and
            0 < (sprite.rect.centerx // 32) < 26 and
            0 < (sprite.rect.centery // 32) < 14]


def line_of_sight(loc, dest_loc, blocking_walls):
    if (not loc) or (not dest_loc):
        return False
    return not any(wall.clipline(loc, dest_loc) for wall in blocking_walls)


def neighbours(loc, dest, blocking_walls):
    # Inflate the walls by one pixel `to make LOS checking work
    inflated_walls = [wall.inflate(2, 2) for wall in blocking_walls]
    # Take the corners of each wall
    important_points = list(chain.from_iterable(
        [(wall.bottomleft, wall.bottomright, wall.topleft, wall.topright) for wall in inflated_walls]
    ))
    important_points.append(dest)
    return [point for point in important_points if line_of_sight(loc, point, blocking_walls) and point != loc]


# TODO: make enemies avoid each other/collide with each other
def theta_star(start_rect, dest, all_sprites):
    """Uses theta* to calculate the optimal path."""

    # Increase the size of the walls to account of the hitbox
    blocking_walls = get_blocking_walls(all_sprites, inflate=(start_rect.width, start_rect.height))

    # Adjust the destination if the destination is unreachable due to it being too close to a wall
    colliding_walls = [wall for wall in blocking_walls if wall.collidepoint(dest)]
    if any(colliding_walls):
        # Find all the walls that are touching this point and combine them
        # Inflate by 1 pixel to make sure LOS check works
        combined_wall = colliding_walls[0].unionall(colliding_walls).inflate(2, 2)

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._path = None
        self.x_y = 0
        self._half_recalculation_delay = 3
        self._current_recalculation_delay = 0

    def lazy_theta_star(self, dest, all_sprites):
        """Calculates the path using theta* but the path is only recalculated roughly every 6 frames."""
        if random.random() > 0.5:
            self._current_recalculation_delay -= 1
        if self._current_recalculation_delay > 0:
            # Path find from the end
            self._path = self._path[:-1] + [dest]
        else:
            # Recalculate the entire path
            self._path = theta_star(self.rect, dest, all_sprites)
            self._current_recalculation_delay = self._half_recalculation_delay

        return self._path

    def move_along_path(self, path, distance, all_sprites):
        """
        Move towards the player, following a path generated by Theta*.
        This function is intended to be used by enemies that will attempt to deal contact damage to the player.
        """

        # this function ignores momentum from collision, so add extra code for that
        distance_left = distance
        for loc in path:
            self.x_y = pygame.Vector2(loc) - pygame.Vector2(self.rect.center)
            if self.x_y.length() < distance_left:
                self.move_respecting_walls(self.x_y, all_sprites)
                distance_left -= self.x_y.length()
            else:
                self.x_y = self.x_y.normalize() * distance_left
                self.move_respecting_walls(self.x_y, all_sprites)
                break

    def handle_damage(self, player, hp_left):
        colliding_bullets = pygame.sprite.spritecollide(self, player.bullets, False)
        for bullet in colliding_bullets:
            if self.hp > 0:
                hp_left -= 1
                bullet.kill()
                if hp_left == 0:
                    self.kill()
                    return 0
        return hp_left


class EnemyBullet(BaseSprite):
    def __init__(self, center, target, speed):
        super().__init__(image_assets='assets/enemy_bullet.png', center=center)
        self.direction = (pygame.Vector2(target) - pygame.Vector2(center)).normalize() * speed

    def update(self, all_sprites, player, gamemap):
        x, y = self.direction
        self.rect.move_ip(x, y)

        walls = [sprite for sprite in all_sprites if isinstance(sprite, Wall)]
        if pygame.sprite.spritecollideany(self, walls):
            self.kill()
            return


class TestEnemy(BaseEnemy):
    def __init__(self, center=(0, 0)):
        super().__init__(image_assets='assets/enemy.png', center=center)
        self.hp = 1

    def update(self, all_sprites, player, game_map):
        self.hp = self.handle_damage(player, self.hp)
        if not self.hp:
            return

        # Random recalculating delay so not all the enemies update at the same time
        path = self.lazy_theta_star(player.rect.center, all_sprites)
        self.move_along_path(path, TEST_ENEMY_SPEED, all_sprites)


class TestShootingEnemy(BaseEnemy):
    def __init__(self, center=(0, 0)):
        super().__init__(image_assets='assets/family_friendly_enemy.png', center=center)
        # Minimum time between attacks
        self.attack_delay = 90
        # If the enemy has already "reloaded" when out of LOS of you, wait this amount of time before actually firing
        self.entered_los_attack_delay = 20
        # If the enemy can immediately see you, do not attack immediately
        self.current_attack_delay = self.attack_delay

        self.hp = 3
        self.bullets = pygame.sprite.Group()

    def update(self, all_sprites, player, game_map):
        self.hp = self.handle_damage(player, self.hp)
        if not self.hp:
            all_sprites.remove(self.bullets)
            self.bullets.empty()
            return

        in_los = line_of_sight(self.rect.center, player.rect.center, get_blocking_walls(all_sprites))
        path = self.lazy_theta_star(player.rect.center, all_sprites)
        self.move_along_path(path, SHOOTING_ENEMY_SPEED, all_sprites)

        if in_los and self.rect.center != player.rect.center:
            self.current_attack_delay -= 1
            if self.current_attack_delay <= 0:
                self.current_attack_delay = self.attack_delay
                all_sprites.remove(self.bullets)
                self.bullets.add(EnemyBullet(self.rect.center, player.rect.center, ENEMY_BULLET_SPEED))
                all_sprites.add(self.bullets)

        elif self.current_attack_delay < self.entered_los_attack_delay:
            self.current_attack_delay = self.entered_los_attack_delay


class TestBoss(BaseEnemy):
    def __init__(self, center=(0, 0)):
        super().__init__(image_assets='assets/cat.png', center=center)
        self.hp = 15

        # Minimum time between attacks
        self.attack_delay = 30
        # If the enemy has already "reloaded" when out of LOS of you, wait this amount of time before actually firing
        self.entered_los_attack_delay = 20
        # If the enemy can immediately see you, do not attack immediately
        self.current_attack_delay = self.attack_delay
        self.bullets = pygame.sprite.Group()

    def update(self, all_sprites, player, game_map):
        self.hp = self.handle_damage(player, self.hp)
        if not self.hp:
            return

        in_los = line_of_sight(self.rect.center, player.rect.center, get_blocking_walls(all_sprites))
        path = self.lazy_theta_star(player.rect.center, all_sprites)
        self.move_along_path(path, BOSS_SPEED, all_sprites)

        if in_los and self.rect.center != player.rect.center:
            self.current_attack_delay -= 1
            if self.current_attack_delay <= 0:
                self.current_attack_delay = self.attack_delay
                all_sprites.remove(self.bullets)

                self.bullets.add(EnemyBullet(self.rect.center, player.rect.center, 8))
                all_sprites.add(self.bullets)

        elif self.current_attack_delay < self.entered_los_attack_delay:
            self.current_attack_delay = self.entered_los_attack_delay
