import math
import pygame
		
class Player():
	def __init__(self):
		self.x, self.y = 10, 10
		self.x_vel = self.y_vel = 0
		self.acceleration = 3

	def check_movement(self, keys):
	    if keys[pygame.K_LEFT]:
	        self.x_vel -= self.acceleration

	    if keys[pygame.K_RIGHT]:
	        self.x_vel += self.acceleration

	    if keys[pygame.K_UP]:
	        self.y_vel -= self.acceleration

	    if keys[pygame.K_DOWN]:
	        self.y_vel += self.acceleration

	def update_physics(self):
		print(self.x_vel, self.y_vel)

		self.x += self.x_vel
		self.y += self.y_vel

		self.x_vel /= 2
		self.y_vel /= 2

	def get_pos(self):
		return (self.x, self.y)

x = Player()