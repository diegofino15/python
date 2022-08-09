import pygame
from pygame import Vector2


class Camera:
    def __init__(self, screenw, screenh, fps, world) -> None:
        self.screenw, self.screenh = screenw, screenh

        self.fps = fps
        self.position = Vector2(0, 0)
        self.delay = 0.1

        self.screen = pygame.display.set_mode((screenw, screenh))
        pygame.display.set_caption("PythCraft")

        self.rect = pygame.Rect(0, 0, screenw, screenh)

        self.movespeed = 10

        self.blocksize = 20
        self.default_blocksize = world.tilesize
        self.world = world

        self.imgs = {}
        self.texture_size = 16
        self.modified = []
    
    def draw(self, image, rect) -> None:
        pos = self.pos_to_cam(self.coord_to_pos(Vector2(rect.left, rect.top)))
        size = self.coord_to_pos(Vector2(image.get_width(), image.get_height()))

        img = pygame.transform.scale(image, (int(size.x), int(size.y)))

        self.screen.blit(img, (int(pos.x), int(pos.y)))
    
    def gen_chunk_img(self, addr):
        chunk = self.world.chunks[addr]

        surf = pygame.Surface((self.texture_size * self.world.chunksize, self.texture_size * self.world.chunksize))
        surf.set_colorkey((0, 0, 0))

        for i_row, row in enumerate(chunk):
            for i_col, tile in enumerate(row):
                if tile is not None and not tile.invisible:
                    surf.blit(tile.image, (i_col * self.texture_size, i_row * self.texture_size))
        
        self.imgs.update({addr: pygame.transform.scale(surf, (self.blocksize * self.world.chunksize, self.blocksize * self.world.chunksize))})
    
    def render(self, world):
        for modified in self.modified: 
            self.gen_chunk_img(modified)
            self.modified.remove(modified)

        minx = (self.rect.left + self.position.x - self.screenw // 2) // self.blocksize
        miny = (self.rect.top + self.position.y - self.screenh // 2) // self.blocksize
        minchunkx = int(minx // world.chunksize)
        minchunky = int(miny // world.chunksize)

        maxx = (self.rect.right + self.position.x - self.screenw // 2) // self.blocksize
        maxy = (self.rect.bottom + self.position.y - self.screenh // 2) // self.blocksize
        maxchunkx = int(maxx // world.chunksize)
        maxchunky = int(maxy // world.chunksize)

        worldkeys = self.world.chunks.keys()
        for i_chunk in range(minchunkx, maxchunkx + 1):
            for j_chunk in range(minchunky, maxchunky + 1):
                addr = (i_chunk, j_chunk)

                if addr in worldkeys:
                    if not addr in self.imgs.keys(): self.gen_chunk_img(addr)

                    x, y = self.coord_to_cam((i_chunk * self.world.chunksize * self.world.tilesize, j_chunk * self.world.chunksize * self.world.tilesize))
                    self.screen.blit(self.imgs[addr], (x, y))
    
    def render2(self, world) -> None:
        minx = (self.rect.left + self.position.x - self.screenw // 2) // self.blocksize
        miny = (self.rect.top + self.position.y - self.screenh // 2) // self.blocksize
        minchunkx = int(minx // world.chunksize)
        minchunky = int(miny // world.chunksize)

        maxx = (self.rect.right + self.position.x - self.screenw // 2) // self.blocksize
        maxy = (self.rect.bottom + self.position.y - self.screenh // 2) // self.blocksize
        maxchunkx = int(maxx // world.chunksize)
        maxchunky = int(maxy // world.chunksize)

        worldkeys = world.chunks.keys()
        for i_chunk in range(minchunkx, maxchunkx + 1):
            for j_chunk in range(minchunky, maxchunky + 1):
                addr = (i_chunk, j_chunk)
                if addr in worldkeys:
                    blocks = world.chunks[addr]
                    for j, row in enumerate(blocks):
                        coordy = j_chunk * world.chunksize + j
                        if miny <= coordy <= maxy: pass
                        else: continue

                        for i, block in enumerate(row):
                            if block is not None:
                                coordx = i_chunk * world.chunksize + i
                                if minx <= coordx <= maxx: pass
                                else: continue

                                newpos = self.pos_to_cam(Vector2(coordx * self.blocksize, coordy * self.blocksize))
                                if self.blocksize != block.image.get_width():
                                    img = pygame.transform.scale(block.image, (int(self.blocksize)+1, int(self.blocksize)+1))
                                else: img = block.image
                                self.screen.blit(img, (newpos.x, newpos.y))

    def get_visible_blocks(self) -> list:
        minx = (self.rect.left + self.position.x - self.screenw // 2) // self.blocksize
        miny = (self.rect.top + self.position.y - self.screenh // 2) // self.blocksize
        minchunkx = int(minx // self.world.chunksize)
        minchunky = int(miny // self.world.chunksize)

        maxx = (self.rect.right + self.position.x - self.screenw // 2) // self.blocksize
        maxy = (self.rect.bottom + self.position.y - self.screenh // 2) // self.blocksize
        maxchunkx = int(maxx // self.world.chunksize)
        maxchunky = int(maxy // self.world.chunksize)

        worldkeys = self.world.chunks.keys()
        blockstoreturn = []
        for i_chunk in range(minchunkx, maxchunkx + 1):
            for j_chunk in range(minchunky, maxchunky + 1):
                addr = (i_chunk, j_chunk)
                if addr in worldkeys:
                    blocks = self.world.chunks[addr]
                    for j, row in enumerate(blocks):
                        coordy = j_chunk * self.world.chunksize + j
                        if miny <= coordy <= maxy: pass
                        else: continue

                        for i, block in enumerate(row):
                            if block is not None:
                                coordx = i_chunk * self.world.chunksize + i
                                if minx <= coordx <= maxx: pass
                                else: continue
                                blockstoreturn.append(block)
        
        return blockstoreturn

    def move(self, target, dt) -> None:
        targetpos = self.coord_to_pos(target.position)

        disx = targetpos.x - self.position.x
        disy = targetpos.y - self.position.y

        pxls_per_frame_x = disx / (self.fps * self.delay)
        pxls_per_frame_y = disy / (self.fps * self.delay)

        self.position.x += pxls_per_frame_x * dt
        self.position.y += pxls_per_frame_y * dt

    def get_block_abs_pos(self, chunkaddr, blockaddr, world) -> Vector2:
        posx = (chunkaddr[0] * world.chunksize + blockaddr[0]) * world.tilesize
        posy = (chunkaddr[1] * world.chunksize + blockaddr[1]) * world.tilesize
        return Vector2(posx, posy)

    def pos_to_cam(self, pos) -> Vector2: return Vector2(pos[0] - self.position.x + self.screenw // 2, pos[1] - self.position.y + self.screenh // 2)
    def cam_to_pos(self, pos) -> Vector2: return Vector2(pos[0] + self.position.x - self.screenw // 2, pos[1] + self.position.y - self.screenh // 2)

    def coord_to_cam(self, pos) -> Vector2: return self.pos_to_cam(self.coord_to_pos(pos))
    def cam_to_coord(self, pos) -> Vector2: return self.pos_to_coord(self.cam_to_pos(pos))

    def pos_to_coord(self, pos) -> Vector2: return Vector2(pos[0] / self.blocksize * self.default_blocksize, pos[1] / self.blocksize * self.default_blocksize)
    def coord_to_pos(self, pos) -> Vector2: return Vector2(pos[0] / self.default_blocksize * self.blocksize, pos[1] / self.default_blocksize * self.blocksize)
