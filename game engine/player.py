from game_engine.sprites.entity import Entity

import pygame



class Player(Entity):
    def __init__(self, pos, size, world, textures_path, speed) -> None:
        super().__init__(pos, size, world, textures_path)

        self.speed = speed
    
    def input(self, pressed):
        self.acceleration.x, self.acceleration.y = 0, 0

        if pressed[pygame.K_LEFT]: self.acceleration.x -= 1
        if pressed[pygame.K_RIGHT]: self.acceleration.x += 1
        if pressed[pygame.K_UP]: self.acceleration.y -= 1
        if pressed[pygame.K_DOWN]: self.acceleration.y += 1

        if self.acceleration.x != 0 or self.acceleration.y != 0: self.acceleration = self.acceleration.normalize()

        self.acceleration.x *= self.speed
        self.acceleration.y *= self.speed








