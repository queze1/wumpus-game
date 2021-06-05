import pygame

from config import *
from lib.Player import Player
from lib.Background import Background
from lib.GameMap import GameMap
from lib.HUD import Minimap, Healthbar

pygame.init()

# Set up window & FPS clock
clock = pygame.time.Clock()

pygame.display.set_caption("game")
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Create objects
player = Player((WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
healthbar = Healthbar(player, center=(166,38))
background = Background()

# Initialize map
game_map = GameMap(10)
minimap = Minimap(game_map, center=(WINDOW_WIDTH - 78, 78))
minimap.render_minimap(game_map)

# maybe use LayeredUpdates()?
all_sprites = pygame.sprite.OrderedUpdates()  # renders sprites in ORDER OF ADDITION
all_sprites.add(background)
all_sprites.add(game_map.environmental_sprites)
all_sprites.add(player)
all_sprites.add(healthbar)
all_sprites.add(minimap)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # Level Handling
    game_map.handle_rooms(all_sprites, player, minimap)

    # Add and update sprites
    all_sprites.clear(window, background.image)
    all_sprites.add(player.bullets)
    all_sprites.remove(minimap)
    all_sprites.add(minimap)
    all_sprites.remove(healthbar)
    all_sprites.add(healthbar)

    if not game_map.is_cleared():
        is_cleared = game_map.enemy_spawner.spawn_enemies(all_sprites)
        if is_cleared:
            game_map.unlock_room(all_sprites)
            game_map.set_cleared(True)

    all_sprites.add(game_map.enemy_spawner.enemies)
    all_sprites.update(all_sprites, player, game_map)

    rects = all_sprites.draw(window)
    pygame.display.update(rects)
    clock.tick(FPS)

pygame.quit()
