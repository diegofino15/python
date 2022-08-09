from pygame.math import Vector2
from pygame import Rect


class Player:
    def __init__(self, id, position, online, size, level, tilesize, friction) -> None:
        self.id = id
        self.position = position
        self.online = online
        self.rotation = 0
        self.rect = Rect(position[0] - size // 2, position[1] - size // 2, size, size)

        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.speed = .4
        self.max_speed = self.speed * 12
        
        self.level = level
        self.lookup_collisions = 5

        self.tilesize = tilesize
        self.friction = friction

        self.moving_left, self.moving_right, self.moving_up, self.moving_down = False, False, False, False

        self.minx, self.miny = size / 2, size / 2
        self.maxx, self.maxy = (len(self.level[0]) * self.tilesize - self.rect.width / 2), (len(self.level) * self.tilesize - self.rect.height / 2)
    
    def update(self, dt):
        self.horizontal_movement(dt)
        self.horizontal_collisions()

        if self.position[0] <= self.minx:
            self.position[0] = self.minx
            self.velocity.x = 0
        elif self.position[0] >= self.maxx:
            self.position[0] = self.maxx
            self.velocity.x = 0
        
        self.vertical_movement(dt)
        self.vertical_collisions()

        if self.position[1] <= self.miny:
            self.position[1] = self.miny
            self.velocity.y = 0
        elif self.position[1] >= self.maxy:
            self.position[1] = self.maxy
            self.velocity.y = 0
    
    def horizontal_movement(self, dt) -> None:
        self.acceleration.x = 0
        if self.moving_left:
            self.acceleration.x -= self.speed
        if self.moving_right:
            self.acceleration.x += self.speed
        
        self.acceleration.x += self.velocity.x * self.friction
        self.velocity.x += self.acceleration.x * dt
        
        if abs(self.velocity.x) < 0.01: self.velocity.x = 0

        self.position[0] += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)
        self.rect.centerx = self.position[0]
    
    def vertical_movement(self, dt):
        self.acceleration.y = 0
        if self.moving_up:
            self.acceleration.y -= self.speed
        if self.moving_down:
            self.acceleration.y += self.speed
        
        self.acceleration.y += self.velocity.y * self.friction
        self.velocity.y += self.acceleration.y * dt
        
        if abs(self.velocity.y) < 0.01: self.velocity.y = 0

        self.position[1] += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)
        self.rect.centery = self.position[1]
    
    # FAIRE FONCTIONNER
    def horizontal_collisions(self):
        for i_row, row in enumerate(self.level):
            for i_col, tile in enumerate(row):
                if tile != 0:
                    x, y = i_col * self.tilesize, i_row * self.tilesize
                    
                    disx = self.position[0] - x
                    disy = self.position[1] - y

                    if (abs(disx) + abs(disy)) <= (self.lookup_collisions * self.tilesize):
                        rect = Rect(x, y, self.tilesize, self.tilesize)
                        if self.colliderect(self.rect, rect):
                            if self.velocity.x > 0:
                                self.position[0] = rect.left - self.rect.width / 2
                                self.rect.centerx = self.position[0]
                                self.velocity.x = 0
                                return
                            elif self.velocity.x < 0:
                                self.position[0] = rect.right + self.rect.width / 2
                                self.rect.centerx = self.position[0]
                                self.velocity.x = 0
                                return
    def vertical_collisions(self):
        for i_row, row in enumerate(self.level):
            for i_col, tile in enumerate(row):
                if tile != 0:
                    x, y = i_col * self.tilesize, i_row * self.tilesize

                    disx = self.position[0] - x
                    disy = self.position[1] - y

                    if (abs(disx) + abs(disy)) <= (self.lookup_collisions * self.tilesize):
                        rect = Rect(x, y, self.tilesize, self.tilesize)
                        if self.colliderect(self.rect, rect):
                            if self.velocity.y > 0:
                                self.rect.bottom = rect.top
                                self.position[1] = self.rect.centery
                                self.velocity.y = 0
                                return
                            elif self.velocity.y < 0:
                                self.rect.top = rect.bottom
                                self.position[1] = self.rect.centery
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



