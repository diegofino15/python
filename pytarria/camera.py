import pygame
from pygame.locals import *
from ressources.textures import blocks, tileset



class Camera:
    def __init__(self, level, main) -> None:
        self.screen = pygame.display.get_surface()
        self.screen_w, self.screen_h = self.screen.get_size()

        self.tilesize = 32
        self.load_textures()

        self.offset = pygame.Vector2(0, 0)
        self.rect = pygame.Rect(0, 0, self.screen_w, self.screen_h)

        self.delay = .5
        self.speed = 1 / 30
        self.speed_ratio = self.tilesize / self.speed

        self.manual_zoom = 2

        self.level = level
        self.chunk_size = self.level.chunk_size

        self.chunk_in = [int(self.offset.x // (self.chunk_size * self.tilesize)), int(self.offset.y // (self.chunk_size * self.tilesize))]
        self.chunk_address = str(self.chunk_in[0]) + ":" + str(self.chunk_in[1])

        self.vision_range = [4, 3]

        self.vision_range[0] = (self.screen_w // (self.chunk_size * self.tilesize)) + 1
        self.vision_range[1] = (self.screen_h // (self.chunk_size * self.tilesize)) + 1

        self.min_y = level.max_world_height * level.chunk_size * self.tilesize
        self.main = main

    def pos_to_cam(self, pos) -> list: return [(pos[0] - self.offset.x + self.screen_w / 2), (pos[1] - self.offset.y + self.screen_h / 2)]
    def cam_to_pos(self, pos) -> list: return [(pos[0] + self.offset.x - self.screen_w / 2), (pos[1] + self.offset.y - self.screen_h / 2)]
    def pos_to_chunk(self, pos) -> list: return [int(pos[0] // self.tilesize // self.chunk_size), int(pos[1] // self.tilesize // self.chunk_size)]

    def load_textures(self) -> None:
        self.tileset = tileset.copy()

        textures = {}
        for i, name in blocks.keys():
            textures.update({i: blocks[(i, name)]})
        
        self.textures = textures

    def move(self, target=None, inputs=False, dt=1/60) -> None:
        if not inputs:
            if target is not None:
                disx = target[0] - self.offset.x
                pxsl_x = disx * self.speed
                self.offset.x += pxsl_x * dt

                disy = target[1] - self.offset.y
                pxls_y = disy * self.speed
                self.offset.y += pxls_y * dt
        else:
            pressed = pygame.key.get_pressed()
            speed = 5
            if pressed[pygame.K_q]: self.offset.x -= speed * dt
            if pressed[pygame.K_d]: self.offset.x += speed * dt
            if pressed[pygame.K_z]: self.offset.y -= speed * dt
            if pressed[pygame.K_s]: self.offset.y += speed * dt

        self.chunk_in = [int(self.offset.x // (self.chunk_size * self.tilesize)), int(self.offset.y // (self.chunk_size * self.tilesize))]
        self.chunk_address = str(self.chunk_in[0]) + ":" + str(self.chunk_in[1])
    
    def get_visible_chunks(self) -> list:
        pos = []

        for i in range(self.vision_range[0]):
            for j in range(self.vision_range[1]):
                x1, x2 = -i, i
                y1, y2 = -j, j

                if x1 != x2:
                    if y1 != y2:
                        pos.append([self.chunk_in[0] + x1, self.chunk_in[1] + y1])
                        pos.append([self.chunk_in[0] + x2, self.chunk_in[1] + y1])
                        pos.append([self.chunk_in[0] + x1, self.chunk_in[1] + y2])
                        pos.append([self.chunk_in[0] + x2, self.chunk_in[1] + y2])
                    else:
                        pos.append([self.chunk_in[0] + x1, self.chunk_in[1] + y1])
                        pos.append([self.chunk_in[0] + x2, self.chunk_in[1] + y1])
                else:
                    if y1 != y2:
                        pos.append([self.chunk_in[0] + x1, self.chunk_in[1] + y1])
                        pos.append([self.chunk_in[0] + x1, self.chunk_in[1] + y2])
                    else:
                        pos.append([self.chunk_in[0] + x1, self.chunk_in[1] + y1])

        return pos

    def render(self, screen, chunks) -> None:
        minx, miny = self.cam_to_pos(self.rect.topleft)
        maxx, maxy = self.cam_to_pos(self.rect.bottomright)
        
        for pos, chunk in chunks:
            offsetx = pos[0] * self.chunk_size
            offsety = pos[1] * self.chunk_size

            for i_row, row in enumerate(chunk):
                for i_col, tile in enumerate(row):
                    if tile == 0: continue

                    x, y = (i_col + offsetx) * self.tilesize, (i_row + offsety) * self.tilesize

                    if x >= maxx or y >= maxy: continue
                    if x < (minx - self.tilesize) or y < (miny - self.tilesize): continue

                    img = self.textures[str(tile)]
                    img = pygame.transform.scale(img, (self.tilesize, self.tilesize))
                    screen.blit(img, self.pos_to_cam((x, y)))

                    if self.main.breaking_block:
                        if (i_col + offsetx) == self.main.mouse_info[3][0]:
                            if (i_row + offsety) == self.main.mouse_info[3][1]:
                                if tile != 4:
                                    surf = pygame.Surface((self.tilesize, self.tilesize))
                                    surf.fill((20, 20, 20))

                                    screen.blit(surf, self.pos_to_cam((x, y)), special_flags=BLEND_RGBA_ADD)

    






