import random
import pygame
from pygame import Vector2
from util.blocks import get_texture, find_texture_pos, items, itemset


class Block(pygame.sprite.Sprite):
    def __init__(self, position, id, size) -> None:
        super().__init__()

        self.position = Vector2(position[0], position[1])
        self.id = id

        self.image = get_texture(find_texture_pos(self.id))
        self.rect = pygame.Rect(self.position.x, self.position.y, size, size)

        self.collidable = True
        self.invisible = False

        self.unbreakable = False



class Item(pygame.sprite.Sprite):
    def __init__(self, position, itemid, size, world, player, actual_time, amount=1) -> None:
        super().__init__()

        self.position = Vector2(position[0], position[1])
        self.itemid = itemid

        self.image = get_texture(items[str(itemid)]["texture"], file=itemset)
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = pygame.Rect(self.position.x, self.position.y, size, size)
        self.elevation = random.randint(5, world.tilesize / 2)
        self.drawrect = pygame.Rect(self.rect.left, self.rect.top - self.elevation, self.rect.width, self.rect.height)

        self.amount = amount

        self.world = world
        self.player = player

        self.acceleration = Vector2(0, world.gravity)
        self.velocity = Vector2(random.randint(0, 50) - 25, 0)
        self.max_y_speed = 15

        self.on_ground = False
        self.existing = True

        self.max_range = 2

        self.exist_time = 15
        self.time_created = actual_time

        self.lookup_collisions = 2
    
    def update(self, dt, actual_time) -> None:
        self.vertical_movement(dt)
        self.vertical_collisions()

        self.horizontal_movement(dt)
        self.horizontal_collisions()

        self.drawrect = pygame.Rect(self.rect.left, self.rect.top - self.elevation, self.rect.width, self.rect.height)

        disx = self.player.position.x - self.position.x
        disy = self.player.position.y - self.position.y
        if abs(disx / self.world.tilesize) + abs(disy / self.world.tilesize) <= self.max_range:
            remaining = self.player.inventory.give(self.itemid, self.amount)
            if remaining == 0: 
                self.existing = False
                return
            else:
                self.amount = remaining
        
        if (self.time_created + self.exist_time) <= actual_time:
            self.existing = False
    
    def horizontal_movement(self, dt) -> None:
        self.acceleration.x = 0        
        self.acceleration.x += self.velocity.x * self.world.friction
        self.velocity.x += self.acceleration.x * dt

        self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)
        self.rect.x = self.position.x
    
    def vertical_movement(self, dt) -> None:
        if not self.on_ground:
            self.velocity.y += self.acceleration.y * dt
            if self.velocity.y > self.max_y_speed: self.velocity.y = self.max_y_speed
            self.position.y += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)
            self.rect.bottom = self.position.y
        
    def horizontal_collisions(self) -> None:
        chunkx = self.position.x // self.world.tilesize // self.world.chunksize
        chunky = self.position.y // self.world.tilesize // self.world.chunksize
        addr = (chunkx, chunky)
        worldkeys = self.world.chunks.keys()
        if addr in worldkeys:
            blocks = self.world.chunks[addr]

            for i_row, row in enumerate(blocks):
                for i_col, block in enumerate(row):
                    if block is not None and block.collidable:
                        x = (i_col + (chunkx * self.world.chunksize)) * self.world.tilesize
                        y = (i_row + (chunky * self.world.chunksize)) * self.world.tilesize

                        disx = self.position.x - x
                        disy = self.position.y - y

                        if (abs(disx) + abs(disy)) <= (self.lookup_collisions * self.world.tilesize):
                            rect = pygame.Rect(x, y, self.world.tilesize, self.world.tilesize)
                            if self.player.colliderect(self.rect, rect):
                                if self.velocity.x > 0:
                                    self.position.x = rect.left - self.rect.width
                                    self.rect.left = self.position.x
                                    self.velocity.x = 0
                                    return
                                elif self.velocity.x < 0:
                                    self.position.x = rect.right
                                    self.rect.left = self.position.x
                                    self.velocity.x = 0
                                    return
    
    def vertical_collisions(self) -> None:
        self.on_ground = False

        chunkx = self.position.x // self.world.tilesize // self.world.chunksize
        chunky = self.position.y // self.world.tilesize // self.world.chunksize
        addr = (chunkx, chunky)

        worldkeys = self.world.chunks.keys()

        if addr in worldkeys:
            blocks = self.world.chunks[addr]
            for i_row, row in enumerate(blocks):
                for i_col, block in enumerate(row):
                    if block is not None and block.collidable:
                        x = (i_col + (chunkx * self.world.chunksize)) * self.world.tilesize
                        y = (i_row + (chunky * self.world.chunksize)) * self.world.tilesize

                        disx = self.position.x - x
                        disy = self.position.y - y

                        if (abs(disx) + abs(disy)) <= (self.lookup_collisions * self.world.tilesize):
                            rect = pygame.Rect(x, y, self.world.tilesize, self.world.tilesize)
                            if self.player.colliderect(self.rect, rect):
                                if self.velocity.y > 0:
                                    self.position.y = rect.top
                                    self.rect.bottom = self.position.y
                                    self.velocity.y = 0
                                    self.on_ground = True
                                    return
                                elif self.velocity.y < 0:
                                    self.rect.top = rect.bottom
                                    self.position.y = self.rect.bottom
                                    self.velocity.y = 0
                                    return







