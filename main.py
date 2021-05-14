import pygame
from lib.Player import Player

pygame.init()

# Set up window & FPS clock
FPS = 60
clock = pygame.time.Clock()
window = pygame.display.set_mode((854, 480))
pygame.display.set_caption("wumpus game")

# changed_rects - list of Rect objects showing where the screen has updated
changed_rects = []
player = Player()

background = pygame.image.load('assets/grokwallpaper.png').convert()
changed_rects.append(window.blit(background, background.get_rect()))


running = True
while running:
    # Process inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # Dirty rect animation https://www.pygame.org/docs/tut/newbieguide.html
    # 1: Find the locations of all the sprites and add them to the list of places which need to be updated on the screen
    changed_rects.append(player.rect)

    # 2: Erase the old sprites with piece of the background
    #window.blit(background, player.rect, player.rect)
    window.blit(background, player.rect, player.rect)

    # 3: Update the locations of the sprites and blit them onto the window in the right order
    player.update()
    window.blit(player.image, player.rect)

    # 4: Add the new locations to the screen updating list
    changed_rects.append(player.rect)

    # 5: Update the screen and clear the rects
    pygame.display.update(changed_rects)
    changed_rects = []

    clock.tick(FPS)


pygame.quit()
