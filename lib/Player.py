import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, center_x=0, center_y=0):
        super().__init__()
        self.image = pygame.image.load('assets/stevencrowder.jpg').convert()

        self.rect = self.image.get_rect()
        self.rect.center = (center_x - self.rect.width/2, center_y - self.rect.height/2)

        self.speed = 7
        self.x_vel, self.y_vel = 0, 0

    def update(self):
        self.x_vel = 0
        self.y_vel = 0

        self.handle_movement()

        self.rect.move_ip(self.x_vel, self.y_vel)

    def handle_movement(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_w]:
            self.y_vel -= self.speed
        if keys_pressed[pygame.K_s]:
            self.y_vel += self.speed
        if keys_pressed[pygame.K_d]:
            self.x_vel += self.speed
        if keys_pressed[pygame.K_a]:
            self.x_vel -= self.speed

        # If the player is moving diagonally, divide their speeds by sqrt(2) to keep the speed the same
        if self.x_vel and self.y_vel:
            self.x_vel /= 2 ** 0.5
            self.y_vel /= 2 ** 0.5