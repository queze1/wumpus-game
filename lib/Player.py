import pygame


class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__(self)

		self.image = pygame.image.load('assets/stevencrowder.jpg')
		self.rect = self.image.get_rect()

	def update(self):
		pass

