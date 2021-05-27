import pygame

from config import *
from lib.Player import Player
from lib.GameMap import GameMap


pygame.init()

# Set up window & FPS clock
clock = pygame.time.Clock()

pygame.display.set_caption("wumpus game")
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Create objects
player = Player((WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
background = pygame.image.load('assets/grokwallpaper.png').convert()

# Initialize map
game_map = GameMap(12)

# maybe use LayeredUpdates()?
all_sprites = pygame.sprite.OrderedUpdates()  # renders sprites in ORDER OF ADDITION
all_sprites.add(game_map.environmental_sprites)
all_sprites.add(player)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # Level Handling
    direction_exited = game_map.check_exited(player.rect)
    if direction_exited:
        # Reset player location
        x_change, y_change = direction_exited
        player.rect.x -= x_change * WINDOW_WIDTH
        player.rect.y -= y_change * WINDOW_HEIGHT

        # Change location
        game_map.move_player(direction_exited)
        print(game_map.player_location)

        # Change level sprites depending on player location
        all_sprites.remove(player.friendly_bullets)
        player.friendly_bullets.empty()
        all_sprites.remove(game_map.environmental_sprites)
        all_sprites.remove(game_map.enemy_spawner.enemies)
        game_map.change_room()
        all_sprites.add(game_map.environmental_sprites)

    # Add and update sprites
    all_sprites.clear(window, background)
    all_sprites.add(player.friendly_bullets)
    if not game_map.is_cleared():
        is_cleared = game_map.enemy_spawner.update_enemies(all_sprites)
        game_map.set_cleared(is_cleared)

    all_sprites.add(game_map.enemy_spawner.enemies)
    all_sprites.update(all_sprites)

    rects = all_sprites.draw(window)
    pygame.display.update(rects)
    clock.tick(FPS)

pygame.quit()
