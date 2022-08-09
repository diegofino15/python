import pygame
from pygame import Vector2


class Entity(pygame.sprite.Sprite):
    def __init__(self, gravity, friction, speed, jump_height, world, pos=Vector2(0, 0), vel=Vector2(0, 0)) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()

        self.moving_left, self.moving_right = False, False

        self.is_jumping, self.on_ground = False, False
        self.gravity, self.friction = gravity, friction

        self.position, self.velocity = pos, vel
        self.acceleration = Vector2(0, self.gravity)

        self.speed = speed
        self.max_speed = self.speed * 12
        self.jump_height = jump_height
        self.max_y_speed = self.jump_height * 2

        self.world = world

        self.lookup_collisions = 5
    
    def get_pos(self) -> Vector2: return Vector2(self.position.x, self.position.y)
    
    def update(self, dt) -> None:
        self.vertical_movement(dt)
        self.vertical_collisions()
        
        self.horizontal_movement(dt)
        self.horizontal_collisions()
    
    def horizontal_movement(self, dt) -> None:
        self.acceleration.x = 0
        if self.moving_left:
            self.acceleration.x -= self.speed
        if self.moving_right:
            self.acceleration.x += self.speed
        
        self.acceleration.x += self.velocity.x * self.friction
        self.velocity.x += self.acceleration.x * dt
        self.limit_velocity(self.max_speed)

        self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)
        self.rect.x = self.position.x
    
    def vertical_movement(self, dt) -> None:
        self.velocity.y += self.acceleration.y * dt
        if self.velocity.y > self.max_y_speed: self.velocity.y = self.max_y_speed

        self.position.y += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)
        self.rect.bottom = self.position.y

    def limit_velocity(self, max_vel) -> None:
        min(-max_vel, max(self.velocity.x, max_vel))
        if abs(self.velocity.x) < 0.01: self.velocity.x = 0
    
    def jump(self) -> None:
        if self.on_ground:
            self.is_jumping = True
            self.velocity.y -= self.jump_height
            self.on_ground = False
    
    def horizontal_collisions(self) -> None:
        minx = self.rect.left // self.world.tilesize - 1
        maxx = self.rect.right // self.world.tilesize + 1

        miny = self.rect.top // self.world.tilesize - 1
        maxy = self.rect.bottom // self.world.tilesize + 1

        minchunk = (int(minx // self.world.chunksize), int(miny // self.world.chunksize))
        maxchunk = (int(maxx // self.world.chunksize), int(maxy // self.world.chunksize))
        
        worldkeys = self.world.chunks.keys()
        for i_chunk in range(minchunk[0], maxchunk[0] + 1):
            for j_chunk in range(minchunk[1], maxchunk[1] + 1):
                addr = (i_chunk, j_chunk)

                if addr in worldkeys:
                    blocks = self.world.chunks[addr]

                    for i_row, row in enumerate(blocks):
                        for i_col, block in enumerate(row):
                            if block is not None and block.collidable:
                                x = (i_col + (i_chunk * self.world.chunksize)) * self.world.tilesize
                                y = (i_row + (j_chunk * self.world.chunksize)) * self.world.tilesize

                                disx = self.position.x - x
                                disy = self.position.y - y

                                if (abs(disx) + abs(disy)) <= (self.lookup_collisions * self.world.tilesize):
                                    rect = pygame.Rect(x, y, self.world.tilesize, self.world.tilesize)
                                    if self.colliderect(self.rect, rect):
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

        minx = self.rect.left // self.world.tilesize - 1
        maxx = self.rect.right // self.world.tilesize + 1

        miny = self.rect.top // self.world.tilesize - 1
        maxy = self.rect.bottom // self.world.tilesize + 1

        minchunk = (int(minx // self.world.chunksize), int(miny // self.world.chunksize))
        maxchunk = (int(maxx // self.world.chunksize), int(maxy // self.world.chunksize))

        worldkeys = self.world.chunks.keys()
        for i_chunk in range(minchunk[0], maxchunk[0] + 1):
            for j_chunk in range(minchunk[1], maxchunk[1] + 1):
                addr = (i_chunk, j_chunk)

                if addr in worldkeys:
                    blocks = self.world.chunks[addr]
                    for i_row, row in enumerate(blocks):
                        for i_col, block in enumerate(row):
                            if block is not None and block.collidable:
                                x = (i_col + (i_chunk * self.world.chunksize)) * self.world.tilesize
                                y = (i_row + (j_chunk * self.world.chunksize)) * self.world.tilesize

                                disx = self.position.x - x
                                disy = self.position.y - y

                                if (abs(disx) + abs(disy)) <= (self.lookup_collisions * self.world.tilesize):
                                    rect = pygame.Rect(x, y, self.world.tilesize, self.world.tilesize)
                                    if self.colliderect(self.rect, rect):
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

    def colliderect(self, rect, collision) -> bool:
        x, y = rect.topleft
        width, height = rect.width, rect.height

        xcol, ycol = collision.topleft
        widthcol, heightcol = collision.width, collision.height

        if x <= xcol <= (xcol + widthcol) <= (x + width) or x <= xcol < (x + width) or xcol <= x < (xcol + widthcol) <= (x + width) or xcol <= x <= (x + width) <= (xcol + widthcol):
            if y <= ycol <= (ycol + heightcol) <= (y + height) or y <= ycol < (y + height) or ycol <= y < (ycol + heightcol) <= (y + height) or ycol <= y <= (y + height) <= (ycol + heightcol):
                return True
        
        return False




