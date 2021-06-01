from random import randint, choice

import pygame


class ParticleSpawner(pygame.sprite.Group):
	def __init__(self, location, count, p): #p = {velocity, radius, colour}
		super().__init__()
		for _ in range(0, count):
			self.add(Particle(location, 
							  (randint(p['velocity'][0][0], p['velocity'][0][1]), randint(p['velocity'][1][0], p['velocity'][1][1])), 
							  randint(p['radius'][0], p['radius'][1]), 
							  p['colour'],
							  p['decay']))

class Particle(pygame.sprite.Sprite):
	def __init__(self, location, velocity, radius, colour, decay):
		super().__init__()
		self.location = list(location)
		self.velocity = list(velocity)
		self.radius = radius
		self.colour = colour
		self.decay = decay

		self.image = pygame.Surface((self.radius*2, self.radius*2))
		self.image.fill((1,1,1))
		self.image.set_colorkey((1,1,1))
		self.rect = self.image.get_rect()

	def update(self, all_sprites, player, game_map):
		self.location[0] += self.velocity[0]
		self.location[1] += self.velocity[1]
		self.radius -= self.decay

		if self.radius <= 0:
			self.kill()

		self.render_circle()


	def render_circle(self):
		self.rect.center = self.location
		self.image.fill((1,1,1))

		if isinstance(self.colour, list):
			pygame.draw.circle(self.image, choice(self.colour), (self.radius, self.radius), self.radius)
		else:
			pygame.draw.circle(self.image, self.colour, (self.radius, self.radius), self.radius)
		