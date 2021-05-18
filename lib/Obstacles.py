import pygame

class Wall(pygame.sprite.Sprite):
    def __init__(self, center=(0, 0)):
        super().__init__()
        self.image = pygame.image.load('assets/wall.png').convert()
        self.rect = self.image.get_rect(center=center)
