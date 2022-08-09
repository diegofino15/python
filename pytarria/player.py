import pygame, math
from pygame.locals import *



class Player(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, grav, friction, speed, jump_height, tilesize, reach) -> None:
        super().__init__()
        # self.image = pygame.image.load("ressources/player/player.png")
        # self.image = pygame.transform.scale(self.image, (width, height))
        self.image = pygame.Surface((width, height))
        self.image.fill("red")

        self.rect = self.image.get_rect(topleft=pos)

        self.LEFT_KEY, self.RIGHT_KEY, self.FACING_LEFT = False, False, False
        self.is_jumping, self.on_ground = False, False

        self.gravity, self.friction = grav, friction
        self.position, self.velocity = pygame.Vector2(0, 0), pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, self.gravity)

        self.speed = speed
        self.max_fall_speed = self.speed * 30
        self.jump_height = jump_height
        self.lookup_radius = 128
        self.reach = reach

        self.keys = {
            "left": K_q,
            "right": K_d,
            "jump": K_z
        }

        self.speed_ratio = tilesize / self.speed
        self.max_fall_speed_ratio = tilesize / self.max_fall_speed
        self.jump_ratio = tilesize / self.jump_height
        self.grav_ratio = tilesize / self.gravity
        self.size_ratio = [tilesize / width, tilesize / height]
        self.lookup_ratio = tilesize / self.lookup_radius
        self.reach_ration = tilesize / self.reach
    
    def draw(self, surf, cam):
        pos = cam.pos_to_cam(self.rect.topleft)
        img = pygame.transform.scale(self.image, (int(cam.tilesize / self.size_ratio[0]), int(cam.tilesize / self.size_ratio[1])))
        surf.blit(img, pos)

    def update(self, dt, tiles):
        self.vertical_movement(dt)
        self.check_collisionsy(tiles)
        self.horizontal_movement(dt)
        self.check_collisionsx(tiles)
    
    def horizontal_movement(self, dt):
        self.acceleration.x = 0
        if self.LEFT_KEY: self.acceleration.x -= self.speed
        elif self.RIGHT_KEY: self.acceleration.x += self.speed
        
        self.acceleration.x += self.velocity.x * self.friction
        self.velocity.x += self.acceleration.x * dt
        self.limit_velocity(self.speed*10)
        self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)
        self.rect.x = self.position.x
    
    def vertical_movement(self, dt):
        self.velocity.y += self.acceleration.y * dt
        if self.velocity.y > self.max_fall_speed: self.velocity.y = self.max_fall_speed
        self.position.y += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)
        self.rect.bottom = self.position.y
    
    def limit_velocity(self, max_vel):
        self.velocity.x = max(-max_vel, min(self.velocity.x, max_vel))
        if abs(self.velocity.x) < .01: self.velocity.x = 0 
    
    def jump(self):
        if self.on_ground:
            self.is_jumping = True
            self.velocity.y -= self.jump_height
            self.on_ground = False
    
    def check_collisionsx(self, tiles):
        collided = False
        for tile in tiles:
            if not collided:
                if self.rect.colliderect(tile):
                    if self.velocity.x > 0:
                        self.position.x = tile.left - self.rect.w
                        self.rect.x = self.position.x
                        self.velocity.x = 0
                        collided = True
                    elif self.velocity.x < 0:
                        self.position.x = tile.right
                        self.rect.x = self.position.x
                        self.velocity.x = 0
                        collided = True
    
    def check_collisionsy(self, tiles):
        self.on_ground = False
        self.rect.bottom += 1
        collided = False
        for tile in tiles:
            if not collided:
                if self.rect.colliderect(tile):
                    if self.velocity.y > 0:
                        self.on_ground = True
                        self.is_jumping = False
                        self.velocity.y = 0
                        self.position.y = tile.top
                        self.rect.bottom = self.position.y
                        collided = True
                    elif self.velocity.y < 0:
                        self.velocity.y = 0
                        self.position.y = tile.bottom + self.rect.h
                        self.rect.bottom = self.position.y
                        collided = True
            



