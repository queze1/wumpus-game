import pygame

from lib.Player import Player

pygame.init()

clock = pygame.time.Clock()
win = pygame.display.set_mode((500,500))
pygame.display.set_caption("VIDEOG AME")
player = Player()

run = True

while run:
    clock.tick(60)
   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    player.check_movement(keys)
    player.update_physics()

    win.fill((0,0,0))  # Fills the screen with black
    pygame.draw.rect(win, (255,0,0), player.get_pos() + (50,50))   
    pygame.display.update() 
    
pygame.quit()