import pygame

from config import *
from lib.Player import Player
from lib.Obstacles import Wall
from lib.GameMap import GameMap
from lib.Environment import Level


pygame.init()

# Set up window & FPS clock
clock = pygame.time.Clock()

pygame.display.set_caption("wumpus game")
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Create objects and changed_rects
player = Player((WINDOW_WIDTH/2, WINDOW_HEIGHT/2))

background = pygame.image.load('assets/grokwallpaper.png').convert()

# Initialize map
map = GameMap()
level = Level(map.get_room())

all = pygame.sprite.OrderedUpdates() #renders sprites in ORDER OF ADDITION
all.add(level)
all.add(player)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # Level Handling
    direction_exited = map.check_player_exited(player.rect)
    if direction_exited:
        # Reset player location
        x_change, y_change = direction_exited
        player.rect.x -= x_change * (WINDOW_WIDTH + 15)
        player.rect.y -= y_change * (WINDOW_HEIGHT + 15)

        # Change location
        map.move_player(direction_exited)

        # Change level depending on new room
        all.remove(level)
        level.reset_room(map.get_room())
        all.add(level)

    all.clear(window, background)
    all.update()
    all.add(player.friendly_bullets)

    rects = all.draw(window)
    pygame.display.update(rects)

    clock.tick(FPS)

pygame.quit()
