import pygame



class Camera:
    def __init__(self, w, h, world, tilesize) -> None:
        self.display = pygame.Surface((w, h))
        self.w, self.h = w, h

        self.world = world

        self.tilesize = tilesize
        self.texture_size = 16

        self.position = pygame.Vector2(w / 2, h / 2)

        x, y = self.coord_to_pos(self.position)
        self._pos = pygame.Vector2(x, y)

        neww, newh = self.pos_to_coord((w, h))
        self.wworld, self.hworld = neww, newh

        self.rendered_images = {}
        self.need_to_modify = []

    def cam_to_pos(self, pos) -> list: return [pos[0] + self._pos.x - self.w / 2, pos[1] + self._pos.y - self.h / 2]
    def pos_to_cam(self, pos) -> list: return [pos[0] - self._pos.x + self.w / 2, pos[1] - self._pos.y + self.h / 2]
    def coord_to_pos(self, pos) -> list: return [pos[0] / self.world.tilesize * self.tilesize, pos[1] / self.world.tilesize * self.tilesize]
    def pos_to_coord(self, pos) -> list: return [pos[0] / self.tilesize * self.world.tilesize, pos[1] / self.tilesize * self.world.tilesize]
    def cam_to_coord(self, pos) -> list: return self.pos_to_coord(self.cam_to_pos(pos))
    def coord_to_cam(self, pos) -> list: return self.pos_to_cam(self.coord_to_pos(pos))

    def update(self) -> None:
        x, y = self.coord_to_pos(self.position)
        self._pos = pygame.Vector2(x, y)

    def gen_chunk_img(self, addr) -> None:
        surf = pygame.Surface((self.texture_size * self.world.chunksize, self.texture_size * self.world.chunksize))
        surf.set_colorkey((0, 0, 0))

        for i_row, row in enumerate(self.world.chunks[addr]):
            for i_col, tile in enumerate(row):
                if tile.visible:
                    surf.blit(tile.texture, (i_col * self.texture_size, i_row * self.texture_size))
        
        surf = pygame.transform.scale(surf, (self.tilesize * self.world.chunksize, self.tilesize * self.world.chunksize))
        self.rendered_images.update({addr: surf})

    def change_chunk_img(self, addr) -> None:
        for x, y in self.world.modified_blocks[addr]:
            texture = self.world.chunks[addr][y][x].texture
            self.rendered_images[addr].blit(pygame.transform.scale(texture, (self.tilesize, self.tilesize)), (x * self.tilesize, y * self.tilesize))
        self.world.modified_blocks.pop(addr)

    def render(self) -> None:
        self.display.fill((0, 0, 0))

        minx, miny = int((self.position.x - self.wworld / 2) // self.world.tilesize // self.world.chunksize), int((self.position.y - self.hworld / 2) // self.world.tilesize // self.world.chunksize)
        maxx, maxy = int((self.position.x + self.wworld / 2) // self.world.tilesize // self.world.chunksize), int((self.position.y + self.hworld / 2) // self.world.tilesize // self.world.chunksize)

        for i in range(minx, maxx + 1):
            for j in range(miny, maxy + 1):
                addr = (i, j)
                if addr in self.world.chunks.keys():
                    if not addr in self.rendered_images.keys(): self.gen_chunk_img(addr)
                    elif addr in self.need_to_modify: 
                        self.change_chunk_img(addr)
                        self.need_to_modify.remove(addr)
                    
                    x, y = self.pos_to_cam((i * self.world.chunksize * self.tilesize, j * self.world.chunksize * self.tilesize))
                    self.display.blit(self.rendered_images[addr], (x, y))
            
        for entity in self.world.entities:
            entity.draw(self)

    def move_towards(self, target, dt, delay=0.1) -> None:
        time = delay * 60
        self.position.x += (target.x - self.position.x) / time * dt
        self.position.y += (target.y - self.position.y) / time * dt




