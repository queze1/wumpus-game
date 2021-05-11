import pygame
from lib.Player import Player


pygame.init()

# Set up window
FPS = 60
clock = pygame.time.Clock()
window = pygame.display.set_mode((854,480))
window.fill((255, 255, 255))
pygame.display.set_caption("wumpus game")

player = Player()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
