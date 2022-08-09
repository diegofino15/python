import pygame


class Camera:
    def __init__(self, world, display, tilesize) -> None:
        self.world = world

        self.display = display
        self.w, self.h = self.display.get_size()

        self.tilesize = tilesize
        self.texture_size = 16

        self.worldw, self.worldh = self.w / self.tilesize * self.world.tilesize, self.h / self.tilesize * self.world.tilesize

        self.position = pygame.Vector2(0, 0)
        self._pos = pygame.Vector2(0, 0)

        self.chunks_imgs = {}

    def update(self): self._pos.x, self._pos.y = self.coord_to_pos(self.position)

    def gen_chunk_img(self, addr):
        surf = pygame.Surface((self.texture_size * self.world.chunksize, self.texture_size * self.world.chunksize))

        for i_row, row in enumerate(self.world.chunks[addr]):
            for i_col, tile in enumerate(row):
                surf.blit(tile.texture, (i_col * self.texture_size, i_row * self.texture_size))
        
        size = int(self.tilesize * self.world.chunksize)
        dynamic_surf = pygame.transform.scale(surf, (size, size))
        self.chunks_imgs.update({addr: [dynamic_surf, surf, self.tilesize]})
    
    def render(self):
        min_chunkx = int((self.position.x - self.worldw / 2) // self.world.tilesize // self.world.chunksize)
        min_chunky = int((self.position.y - self.worldh / 2) // self.world.tilesize // self.world.chunksize)
        max_chunkx = int((self.position.x + self.worldw / 2) // self.world.tilesize // self.world.chunksize)
        max_chunky = int((self.position.y + self.worldh / 2) // self.world.tilesize // self.world.chunksize)

        chunks = self.world.chunks.keys()
        imgs = self.chunks_imgs.keys()
        for i in range(min_chunkx - 1, max_chunkx + 2):
            for j in range(min_chunky - 1, max_chunky + 2):
                addr = (i, j)

                if addr in chunks:
                    if not addr in imgs: self.gen_chunk_img(addr)

                    drawpos = self.coord_to_cam(self.world.chunk_to_coord(addr))

                    surf, original_surf, tilesize = self.chunks_imgs[addr]

                    if tilesize != self.tilesize:
                        size = int(self.tilesize * self.world.chunksize)
                        self.chunks_imgs[addr][0] = pygame.transform.scale(original_surf, (size, size))
                        self.chunks_imgs[addr][2] = self.tilesize
                    
                    self.display.blit(self.chunks_imgs[addr][0], drawpos)
        
        for entity in self.world.entities:
            entity.draw(self)
    
    def update_tilesize(self): 
        self.worldw, self.worldh = self.w / self.tilesize * self.world.tilesize, self.h / self.tilesize * self.world.tilesize
        self.update()

    # HELPER FUNCTIONS
    
    def cam_to_pos(self, pos): return [pos[0] + self._pos.x - self.w / 2, pos[1] + self._pos.y - self.h / 2]
    def pos_to_cam(self, pos): return [pos[0] - self._pos.x + self.w / 2, pos[1] - self._pos.y + self.h / 2]

    def pos_to_coord(self, pos): return [pos[0] / self.tilesize * self.world.tilesize, pos[1] / self.tilesize * self.world.tilesize]
    def coord_to_pos(self, pos): return [pos[0] / self.world.tilesize * self.tilesize, pos[1] / self.world.tilesize * self.tilesize]

    def coord_to_cam(self, pos): return self.pos_to_cam(self.coord_to_pos(pos))
    def cam_to_coord(self, pos): return self.pos_to_coord(self.cam_to_pos(pos))
