import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load('assets/stevencrowder.jpg').convert()
        self.rect = self.image.get_rect()

    def update(self):
        keys_pressed = pygame.key.get_pressed()

        # TODO: Make diagonal movement the same speed
        if keys_pressed[pygame.K_w]:
            self.rect.move_ip(0, -10)
        if keys_pressed[pygame.K_s]:
            self.rect.move_ip(0, 10)
        if keys_pressed[pygame.K_d]:
            self.rect.move_ip(10, 0)
        if keys_pressed[pygame.K_a]:
            self.rect.move_ip(-10, 0)
