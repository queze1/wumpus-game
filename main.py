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
    game_map.handle_rooms(all_sprites, player)

    # Add and update sprites
    all_sprites.clear(window, background)
    all_sprites.add(player.friendly_bullets)
    if not game_map.is_cleared():
        is_cleared = game_map.enemy_spawner.spawn_enemies(all_sprites)
        if is_cleared:
            game_map.unlock_room(all_sprites)
            game_map.set_cleared(True)

    all_sprites.add(game_map.enemy_spawner.enemies)
    all_sprites.update(all_sprites, player)

    rects = all_sprites.draw(window)
    pygame.display.update(rects)
    clock.tick(FPS)

pygame.quit()
