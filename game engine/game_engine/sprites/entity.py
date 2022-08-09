import pygame, os


class Entity:
    def __init__(self, pos, size, world, textures_path) -> None:
        super().__init__()

        self.position = pygame.Vector2(pos[0], pos[1])
        self.rect = pygame.Rect(self.position.x - size[0] // 2, self.position.y - size[1] // 2, size[0], size[1])

        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)

        self.max_vel = 45 / 32 * world.tilesize

        self.world = world

        self.lookup_col = 10 * self.world.tilesize

        self.textures_path = textures_path
        self.load_textures(self.textures_path)

    def load_textures(self, path):
        self.textures = []
        for root, _, files in os.walk(path, topdown=False):
            for name in sorted(files):
                fullpath = os.path.join(root, name)
                if fullpath[-4:] == ".png":
                    img = pygame.image.load(fullpath)
                    self.textures.append(pygame.transform.scale(img, (self.rect.width, self.rect.height)))  

        self.cooldown_animations = 1 / len(self.textures)
        self.last_animation = -self.cooldown_animations
        self.current_animation = 0    

    def update(self, dt, actual_time):
        self.vertical_movement(dt)
        self.check_collisionsy()
        self.horizontal_movement(dt)
        self.check_collisionsx()

        if (self.last_animation + self.cooldown_animations) <= actual_time:
            self.last_animation = actual_time
            self.current_animation += 1
        
        if self.current_animation >= len(self.textures): self.current_animation = 0
    
    def vertical_movement(self, dt) -> None:
        self.acceleration.y += self.velocity.y * self.world.friction
        self.velocity.y += self.acceleration.y * dt
        self.position.y += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)
        self.rect.centery = self.position.y
    
    def horizontal_movement(self, dt) -> None:
        self.acceleration.x += self.velocity.x * self.world.friction
        self.velocity.x += self.acceleration.x * dt
        self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)
        self.rect.centerx = self.position.x

    def check_collisionsx(self) -> None:
        min_chunkx, min_chunky = self.world.coord_to_chunk(self.rect.topleft)
        max_chunkx, max_chunky = self.world.coord_to_chunk(self.rect.bottomright)

        worldkeys = self.world.chunks.keys()
        for i_chunk in range(min_chunkx, max_chunkx + 1):
            for j_chunk in range(min_chunky, max_chunky + 1):
                addr = (i_chunk, j_chunk)

                if addr in worldkeys:
                    chunk = self.world.chunks[addr]

                    for row in chunk:
                        for tile in row:

                            if not tile.collider: continue

                            disx = self.position.x - tile.rect.centerx
                            disy = self.position.y - tile.rect.centery

                            if abs(disx) + abs(disy) <= self.lookup_col:
                                if self.rect.colliderect(tile.rect):
                                    if self.velocity.x > 0:
                                        if tile.rigid:
                                            self.position.x = tile.rect.left - self.rect.width / 2
                                            self.rect.centerx = self.position.x
                                            self.velocity.x = 0
                                        tile.collide(self)
                                        return
                                    elif self.velocity.x < 0:
                                        if tile.rigid:
                                            self.position.x = tile.rect.right + self.rect.width / 2
                                            self.rect.centerx = self.position.x
                                            self.velocity.x = 0
                                        tile.collide(self)
                                        return
    
    def check_collisionsy(self) -> None:
        min_chunkx, min_chunky = self.world.coord_to_chunk(self.rect.topleft)
        max_chunkx, max_chunky = self.world.coord_to_chunk(self.rect.bottomright)

        worldkeys = self.world.chunks.keys()
        for i_chunk in range(min_chunkx, max_chunkx + 1):
            for j_chunk in range(min_chunky, max_chunky + 1):
                addr = (i_chunk, j_chunk)

                if addr in worldkeys:
                    chunk = self.world.chunks[addr]

                    for row in chunk:
                        for tile in row:

                            if not tile.collider: continue

                            disx = self.position.x - tile.rect.centerx
                            disy = self.position.y - tile.rect.centery

                            if abs(disx) + abs(disy) <= self.lookup_col:
                                if self.rect.colliderect(tile.rect):
                                    if self.velocity.y > 0:
                                        if tile.rigid:
                                            self.position.y = tile.rect.top - self.rect.height / 2
                                            self.rect.centery = self.position.y
                                            self.velocity.y = 0
                                        tile.collide(self)
                                        return
                                    elif self.velocity.y < 0:
                                        if tile.rigid:
                                            self.position.y = tile.rect.bottom + self.rect.height / 2
                                            self.rect.centery = self.position.y
                                            self.velocity.y = 0
                                        tile.collide(self)
                                        return
    
    def draw(self, cam) -> None:
        pos = cam.coord_to_cam(self.rect.topleft)
        texture = self.textures[self.current_animation]
        x, y = cam.coord_to_pos((self.rect.width, self.rect.height))
        if pos[0] > cam.w or pos[1] > cam.h or pos[0] < -x or pos[1] < -y: return
        cam.display.blit(pygame.transform.scale(texture, (int(x), int(y))), pos)




