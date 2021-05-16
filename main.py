import pygame

from config import *
from lib.Player import Player
from lib.GameMap import GameMap


pygame.init()

# Set up window & FPS clock
clock = pygame.time.Clock()

pygame.display.set_caption("wumpus game")
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Create objects and changed_rects
changed_rects = []
player = Player(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)

background = pygame.image.load('assets/grokwallpaper.png').convert()
changed_rects.append(window.blit(background, background.get_rect()))

# Initialize map
map = GameMap()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # Level Handling
    direction_exited = map.check_player_exited(player.rect)
    if direction_exited:
        player.rect.x = WINDOW_WIDTH/2 - player.rect.width/2
        player.rect.y = WINDOW_HEIGHT/2 - player.rect.height/2
        map.move_player(direction_exited)


    # 1: Erase the old sprites with piece of the background and add their locations to the screen updating list
    changed_rects.append(window.blit(background, player.rect, player.rect))
    changed_rects += window.blits([(background, bullet.rect, bullet.rect) for bullet in player.friendly_bullets])

    # 2: Update the locations of the sprites and blit them onto the window in the right order
    player.update()
    player.friendly_bullets.update()
    player.friendly_bullets.draw(window)
    window.blit(player.image, player.rect)

    # 3: Add the new locations to the screen updating list
    changed_rects.append(player.rect)
    changed_rects += [bullet.rect for bullet in player.friendly_bullets]

    # 4: Update the screen and clear the rects
    pygame.display.update(changed_rects)
    changed_rects = []

    clock.tick(FPS)

pygame.quit()
