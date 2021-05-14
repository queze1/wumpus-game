import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, center_x=0, center_y=0):
        super().__init__()
        self.image = pygame.image.load('assets/stevencrowder.jpg').convert()

        self.rect = self.image.get_rect()
        self.rect.center = (center_x, center_y)

    def update(self):
        x = 0
        y = 0
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_w]:
            y -= 10
        if keys_pressed[pygame.K_s]:
            y += 10
        if keys_pressed[pygame.K_d]:
            x += 10
        if keys_pressed[pygame.K_a]:
            x -= 10

        # If the player is moving diagonally, divide their speeds by sqrt(2) to keep the speed the same
        if x and y:
            x /= 2 ** 0.5
            y /= 2 ** 0.5

        self.rect.move_ip(x, y)
