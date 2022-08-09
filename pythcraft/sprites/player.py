from sprites.entity import Entity
from inventory import Inventory
from pygame import Vector2
import pygame


class Player(Entity):
    def __init__(self, gravity, friction, speed, jump_height, size, world, game, pos=Vector2(0, 0), vel=Vector2(0, 0)) -> None:
        super().__init__(gravity, friction, speed, jump_height, world, pos, vel)

        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()

        self.inventory = Inventory(Vector2(20, 20), 10, 50, 5, game)
        self.breaking_block = False
        self.time_begin_breaking = 0
        self.time_to_break_block = 0
        self.block_breaking = None
        self.slot_breaking = 0

        self.game = game
    
    def input(self, pressed) -> None:
        if pressed[pygame.K_q]: self.moving_left = True
        else: self.moving_left = False
        if pressed[pygame.K_d]: self.moving_right = True
        else: self.moving_right = False
        if pressed[pygame.K_z]: self.jump()
    
    




