import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load('assets/stevencrowder.jpg').convert()
        self.rect = self.image.get_rect()

    def update(self):
        pass
