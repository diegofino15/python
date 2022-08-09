import pygame



class Camera:
    def __init__(self, display, scene, tilesize=32, fps=60) -> None:
        self.display = display
        self.w, self.h = self.display.get_size()

        self.position = [0, 0]
        self.world_position = pygame.Vector2(0, 0)

        self.velocity = pygame.Vector2(0, 0)

        self.fps = fps

        # Visual tilesize
        self.tilesize = tilesize
        self.texture_size = 16

        self.scene = scene

        self.chunks_imgs = {}

        self.w_word, self.h_world = self.pos_to_coord((self.w, self.h))
        self.invisible_color = (255, 255, 254)

        self.chunks_to_generate = []
        self.chunks_to_modify = {}
    
    def update(self, dt):
        self.position = self.coord_to_pos(self.world_position)

        self.velocity.x += self.velocity.x * self.scene.friction
        self.velocity.y += self.velocity.y * self.scene.friction

        self.world_position.x += self.velocity.x * dt
        self.world_position.y += self.velocity.y * dt

    def gen_chunk_img(self, addr):
        if addr in self.scene.chunks.keys():
            surf = pygame.Surface((self.texture_size * self.scene.chunksize, self.texture_size * self.scene.chunksize))
            surf.fill(self.invisible_color)
            surf.set_colorkey(self.invisible_color)

            for i_row, row in enumerate(self.scene.chunks[addr]):
                for i_col, tile in enumerate(row):
                    if tile.visible:
                        drawpos = i_col * self.texture_size, i_row * self.texture_size
                        surf.blit(tile.texture, drawpos)
            
            surf = pygame.transform.scale(surf, (int(self.tilesize * self.scene.chunksize), int(self.tilesize * self.scene.chunksize)))
            self.chunks_imgs.update({addr: surf})
    
    def change_chunk_img(self, addr):
        to_remove = []
        for key in self.chunks_to_modify.keys():
            if key[0] == addr[0] and key[1] == addr[1]:
                for pos in self.chunks_to_modify[key]:
                    abspos = (int(addr[0] * self.scene.chunksize + pos[0]), int(addr[1] * self.scene.chunksize + pos[1]))
                    block = self.scene.getblock(abspos)

                    drawpos = pos[0] * self.tilesize, pos[1] * self.tilesize
                    if block is not None and block.visible:
                        texture = pygame.transform.scale(block.texture, (self.tilesize, self.tilesize))
                        self.chunks_imgs[addr].blit(texture, drawpos)
                    else:
                        pygame.draw.rect(self.chunks_imgs[addr], (0, 0, 0), (drawpos[0], drawpos[1], self.tilesize, self.tilesize))
                    
                to_remove.append(key)
        
        for address in to_remove: self.chunks_to_modify.pop(address)

    def render(self):
        self.display.fill((0, 0, 0))

        min_chunkx, min_chunky = self.coord_to_chunk((self.world_position[0] - self.w_word / 2, self.world_position[1] - self.h_world / 2))
        max_chunkx, max_chunky = self.coord_to_chunk((self.world_position[0] + self.w_word / 2, self.world_position[1] + self.h_world / 2))

        worldkeys = self.scene.chunks.keys()
        imgskeys = self.chunks_imgs.keys()
        modified = self.chunks_to_modify.keys()

        for i_chunk in range(int(min_chunkx - 1), int(max_chunkx + 2)):
            for j_chunk in range(int(min_chunky - 1), int(max_chunky + 2)):
                addr = (i_chunk, j_chunk)

                if addr in worldkeys:
                    if not addr in imgskeys:
                        self.gen_chunk_img(addr)
                    elif addr in self.chunks_to_generate: 
                        self.gen_chunk_img(addr)
                        self.chunks_to_generate.remove(addr)
                    elif addr in modified: 
                        self.change_chunk_img(addr)
                    
                    drawpos = self.chunk_to_cam(addr)
                    self.display.blit(self.chunks_imgs[addr], drawpos)
        
        for entity in self.scene.entities:
            entity.draw(self)

    def smooth_follow(self, target, delay, dt):
        disx = target[0] - self.world_position.x
        disy = target[1] - self.world_position.y

        pxlsx = disx / (delay * self.fps)
        pxlsy = disy / (delay * self.fps)

        self.velocity.x += pxlsx * dt
        self.velocity.y += pxlsy * dt

    # HELPER FUNCTIONS
    def cam_to_pos(self, pos): return [pos[0] + self.position[0] - self.w / 2, pos[1] + self.position[1] - self.h / 2]
    def pos_to_cam(self, pos): return [pos[0] - self.position[0] + self.w / 2, pos[1] - self.position[1] + self.h / 2]
    def pos_to_coord(self, pos): return [pos[0] / self.tilesize * self.scene.tilesize, pos[1] / self.tilesize * self.scene.tilesize]
    def coord_to_pos(self, pos): return [pos[0] / self.scene.tilesize * self.tilesize, pos[1] / self.scene.tilesize * self.tilesize]
    def cam_to_coord(self, pos): return self.pos_to_coord(self.cam_to_pos(pos))
    def coord_to_cam(self, pos): return self.pos_to_cam(self.coord_to_pos(pos))
    def coord_to_chunk(self, pos): return [int(pos[0] // self.scene.tilesize // self.scene.chunksize), int(pos[1] // self.scene.tilesize // self.scene.chunksize)]
    def chunk_to_coord(self, pos): return [int(pos[0] * self.scene.tilesize * self.scene.chunksize), int(pos[1] * self.scene.tilesize * self.scene.chunksize)]
    def chunk_to_pos(self, pos): return self.coord_to_pos(self.chunk_to_coord(pos))
    def pos_to_chunk(self, pos): return self.coord_to_chunk(self.pos_to_coord(pos))
    def chunk_to_cam(self, pos): return self.coord_to_cam(self.chunk_to_coord(pos))
    def cam_to_chunk(self, pos): return self.coord_to_chunk(self.cam_to_coord(pos))



