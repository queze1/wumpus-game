import pygame
from lib.Player import Player


pygame.init()

# Set up window & FPS clock
FPS = 60
clock = pygame.time.Clock()
window = pygame.display.set_mode((854,480))
pygame.display.set_caption("wumpus game")

# changed_rects - list of Rect objects showing where the screen has updated
changed_rects = [window.fill((255, 255, 255))]
player = Player()


running = True
while running:
    # Process inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # TODO: Use dirty rect animation https://www.pygame.org/docs/tut/newbieguide.html
    changed_rect = window.blit(player.image, (10, 10))
    pygame.display.update(changed_rect)
    clock.tick(FPS)

pygame.quit()
