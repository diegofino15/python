from copy import deepcopy
import pygame, json, queue
from gui import Scroll


class Filler:
    def floodFill(self, matrix, i, j, new_data):
        self.blocks_filled = 0

        if matrix is None or matrix[j][i] == new_data: return matrix
        
        original = deepcopy(matrix)
        try: self.fillbfs(matrix, i, j, matrix[j][i], new_data)
        except RecursionError: 
            return original
        
        return matrix
    
    def filldfs(self, matrix, i, j, initial, new_data):
        if i < 0 or j < 0 or i >= len(matrix[0]) or j >= len(matrix) or matrix[j][i] != initial: return

        matrix[j][i] = new_data
        self.blocks_filled += 1

        self.fill(matrix, i + 1, j, initial, new_data) # Right
        self.fill(matrix, i - 1, j, initial, new_data) # Left
        self.fill(matrix, i, j + 1, initial, new_data) # Down
        self.fill(matrix, i, j - 1, initial, new_data) # Up

    def fillbfs(self, matrix, i, j, initial, new_data) -> None:
        if i < 0 or j < 0 or i >= len(matrix[0]) or j >= len(matrix) or matrix[j][i] != initial: return
        
        file2 = queue.Queue()

        file2.put((i, j))
        while not file2.empty():
            current_i, current_j = file2.get()
            
            if matrix[current_j][current_i] == new_data: continue
            matrix[current_j][current_i] = new_data

            for di,dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_i = di + current_i
                new_j = dj + current_j

                if new_i < 0 or new_j < 0 or \
                    new_i >= len(matrix[0]) or new_j >= len(matrix) or \
                        matrix[new_j][new_i] != initial or \
                            matrix[new_j][new_i] == "filling": continue
                
                file2.put((new_i, new_j))
                matrix[new_j][new_i] = "filling"



class LevelEditor:
    def __init__(self) -> None:
        self.tilesize = 25

        self.screen_w = 1280
        self.screen_h = 720
        
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))

        self.running = True
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.dt = 1 / self.fps

        self.levelsizex = 150
        self.levelsizey = 100
        self.border_rect = pygame.Rect(0, 0, self.levelsizex * self.tilesize, self.levelsizey * self.tilesize)

        self.actual_tileset = 0
        self.blocks = self.load_tileset()

        self.cam_offset = pygame.Vector2(self.levelsizex * self.tilesize / 2, self.levelsizey * self.tilesize / 2)
        self.cam_display = pygame.Surface((self.screen_w, self.screen_h))
        self.cam_speed = 300

        self.placing = False
        self.erasing = False
        self.selectioning = False
        self.filler = Filler()

        self.first_selec_pos = [0, 0]
        self.second_selec_pos = [0, 0]
        self.ended_selec = False

        self.actual_block = "center"

        self.gui_color = (71, 66, 80)
        self.tileset_chooser_rect = pygame.Rect(0, 0, 200, self.screen_h)
        self.tile_chooser_rect = pygame.Rect(200, self.screen_h - 100, self.screen_w - 200, 100)
        pygame.font.init()
        self.font = pygame.font.Font("Arial.ttf", 25)
        self.littlefont = pygame.font.Font("Arial.ttf", 15)

        self.tileset_choosing_rects = [
            [" tileset 1 ", 0],
            [" tileset 2 ", 1]
        ]

        for i, tileset in enumerate(self.tileset_choosing_rects):
            surf = self.font.render(tileset[0], True, "white")
            self.tileset_choosing_rects[i].append(surf)
        
        offsety = 20
        offsetx = 20
        for i in range(len(self.tileset_choosing_rects)):
            x = self.tileset_chooser_rect.left + offsetx
            y = self.tileset_chooser_rect.top + (i * offsetx) + offsetx + (i * surf.get_height())

            rect = pygame.Rect(x, y, surf.get_width(), surf.get_height())
            self.tileset_choosing_rects[i].append(rect)

        # Block choosing
        self.block_choosing_rects = {}
        offsety = 20
        offsetx = 20
        size = 64
        for i, index in enumerate(self.blocks.keys()):
            x = self.tile_chooser_rect.left + (i * offsetx) + offsetx + (i * size)
            y = self.tile_chooser_rect.top + offsety

            rect = pygame.Rect(x, y, size, size)
            self.block_choosing_rects.update({index: rect})
        
        self.noneblock = pygame.Rect(x + offsetx + size, y, size, size)

        self.zoom_scroll = Scroll((self.tile_chooser_rect.right - 220, self.tile_chooser_rect.top + 20), 200, 30, 25, min=8, max=64, color=self.gui_color, outline_color="grey", bar_color="#6a6a6a", bar_size=100)
        #self.zoom_scroll = Scroll((self.screen_w - 30 - offsetx, offsety), 30, self.screen_h - offsety * 2 - self.tile_chooser_rect.height, 25, 8, 64, bar_size=100, axis="vertical")

        self.first_pos_multiplier = self.tilesize
        self.cam_rect = pygame.Rect(self.tileset_chooser_rect.right, 0, self.screen_w - self.tileset_chooser_rect.width, self.screen_h - self.tile_chooser_rect.height)

    def set(self, level):
        self.running = True

        self.actual_map = level
        
        try: self.matrix = self.load_map()
        except: self.matrix = [[None for i in range(self.levelsizex)] for j in range(self.levelsizey)]
        self.save()


    def pos_to_cam(self, pos): return [pos[0] - self.cam_offset.x + self.screen_w / 2, pos[1] - self.cam_offset.y + self.screen_h / 2]
    def cam_to_pos(self, pos): return [pos[0] + self.cam_offset.x - self.screen_w / 2, pos[1] + self.cam_offset.y - self.screen_h / 2]
    def matrix_pos(self, pos): return [int(pos[0] // self.tilesize), int(pos[1] // self.tilesize)]
    def world_pos(self, pos): return [pos[0] * self.tilesize, pos[1] * self.tilesize]

    def load_map(self):
        with open(f"./levels/level_{self.actual_map}.json") as file:
            level = json.load(file)
            file.close()
        
        return level["level"]

    def load_tileset(self):
        tileset = pygame.image.load(f"./ressources/tileset0.png")

        x = self.actual_tileset * 16
        blocks = {
            "up": self.get_texture(tileset, x, 0, (self.tilesize, self.tilesize)),
            "down": self.get_texture(tileset, x, 16, (self.tilesize, self.tilesize)),
            "left": self.get_texture(tileset, x, 32, (self.tilesize, self.tilesize)),
            "right": self.get_texture(tileset, x, 48, (self.tilesize, self.tilesize)),

            "upleft": self.get_texture(tileset, x, 64, (self.tilesize, self.tilesize)),
            "upright": self.get_texture(tileset, x, 80, (self.tilesize, self.tilesize)),
            "downleft": self.get_texture(tileset, x, 96, (self.tilesize, self.tilesize)),
            "downright": self.get_texture(tileset, x, 112, (self.tilesize, self.tilesize)),

            "center": self.get_texture(tileset, x, 128, (self.tilesize, self.tilesize))
        }

        return blocks

    def get_texture(self, tileset, x, y, size):
        image = tileset.subsurface([x, y, 16, 16])
        image = pygame.transform.scale(image, size)
        image.set_colorkey((0, 0, 0))
        return image
    
    def refresh_screen(self):
        minx, miny = self.matrix_pos(self.cam_to_pos(self.cam_rect.topleft))
        maxx, maxy = self.matrix_pos(self.cam_to_pos(self.cam_rect.bottomright))

        minx2 = int(min(self.first_selec_pos[0], self.second_selec_pos[0]))
        miny2 = int(min(self.first_selec_pos[1], self.second_selec_pos[1]))
        maxx2 = int(max(self.first_selec_pos[0], self.second_selec_pos[0]))
        maxy2 = int(max(self.first_selec_pos[1], self.second_selec_pos[1]))

        self.cam_display.fill((0, 0, 0))
        for i in range(minx, maxx + 1):
            for j in range(miny, maxy + 1):
                try: tile = self.matrix[j][i]
                except: continue
                if tile is None: continue
                if i < 0 or j < 0 or i >= self.levelsizex or j >= self.levelsizey: continue

                x, y = self.pos_to_cam((i * self.tilesize, j * self.tilesize))
                img = pygame.transform.scale(self.blocks[tile], (self.tilesize, self.tilesize))
                self.screen.blit(img, (x, y))

                if self.selectioning or self.ended_selec:
                    if minx2 <= i <= maxx2:
                        if miny2 <= j <= maxy2:
                            pygame.draw.rect(self.screen, "grey", (x, y, self.tilesize, self.tilesize), width=2, border_radius=4)



        mscoord = self.cam_to_pos(self.mspos)
        msmatrix = self.matrix_pos(mscoord)
        newmspos = self.pos_to_cam((msmatrix[0] * self.tilesize, msmatrix[1] * self.tilesize))
        if not self.selectioning: pygame.draw.rect(self.screen, "white", (newmspos[0], newmspos[1], self.tilesize, self.tilesize), width=3)

        if self.ended_selec or self.selectioning:
            multi = self.tilesize / self.first_pos_multiplier
            firstpos = self.pos_to_cam((self.visual_first_pos[0] * multi, self.visual_first_pos[1] * multi))
            secondpos = self.pos_to_cam((self.visual_second_pos[0] * multi, self.visual_second_pos[1] * multi))
            x = min(firstpos[0], secondpos[0])
            y = min(firstpos[1], secondpos[1])
            width = abs(secondpos[0] - firstpos[0])
            height = abs(secondpos[1] - firstpos[1])
            pygame.draw.rect(self.screen, "orange", (x, y, width, height), width=3)

            
        x, y = self.pos_to_cam(self.border_rect.topleft)
        pygame.draw.rect(self.screen, "red", (x, y, self.border_rect.width, self.border_rect.height), width=2)
        
        self.widgets(mscoord, msmatrix)

    def widgets(self, mscoord, msmatrix):
        pygame.draw.rect(self.screen, self.gui_color, self.tileset_chooser_rect)
        pygame.draw.rect(self.screen, self.gui_color, self.tile_chooser_rect)
        pygame.draw.rect(self.screen, "black", self.noneblock)
        for index in self.blocks.keys():
            rect = self.block_choosing_rects[index]

            img = self.blocks[index].copy()
            img = pygame.transform.scale(img, (rect.width, rect.height))

            self.screen.blit(img, rect)

            if index == self.actual_block:
                pygame.draw.rect(self.screen, "white", rect, width=2)
            elif self.actual_block == None:
                pygame.draw.rect(self.screen, "white", self.noneblock, width=2)
        

        for tileset in self.tileset_choosing_rects:
            self.screen.blit(tileset[2], tileset[3])
            if self.actual_tileset == tileset[1]: pygame.draw.rect(self.screen, "white", tileset[3], width=2)
        

        out = not self.tile_chooser_rect.collidepoint(self.mspos) and not self.tileset_chooser_rect.collidepoint(self.mspos)
        outx = True if msmatrix[0] < 0 or msmatrix[0] >= self.levelsizex else False
        outy = True if msmatrix[1] < 0 or msmatrix[1] >= self.levelsizey else False

        label = f"{int(msmatrix[0])}, {int(msmatrix[1])}" if not outx and not outy and out else "--, --"
        surf = self.font.render(label, True, "white")
        self.screen.blit(surf, (self.tileset_chooser_rect.right + 20, 20))

        real_ms_coord = [mscoord[0] / self.tilesize * self.zoom_scroll.get_original_val(), mscoord[1] / self.tilesize * self.zoom_scroll.get_original_val()]
        label = f"{int(real_ms_coord[0])}, {int(real_ms_coord[1])}" if not outx and not outy and out else "--, --"
        surf = self.littlefont.render(label, True, "white")
        self.screen.blit(surf, (self.tileset_chooser_rect.right + 20, 60))

        label = "SAVED" if self.saved else "NOT SAVED"
        color = "green" if self.saved else "red"
        surf = self.font.render(label, True, color)
        self.screen.blit(surf, (self.screen_w - surf.get_width() - 20, 20))

        self.zoom_scroll.draw(self.screen)
        label = f"ZOOM : {round(self.zoom * 10) / 10}"
        surf = self.font.render(label, True, "grey")
        self.screen.blit(surf, (self.screen_w - 20 - surf.get_width(), self.screen_h - 20 - surf.get_height()))

        label = f"LEVEL {self.actual_map}"
        surf = self.font.render(label, True, "white")
        self.screen.blit(surf, (self.tile_chooser_rect.right - surf.get_width() - 10, self.tile_chooser_rect.top - surf.get_height() - 10))
    
    def rearrange(self):
        minx = min(self.first_selec_pos[0], self.second_selec_pos[0])
        maxx = max(self.first_selec_pos[0], self.second_selec_pos[0])
        miny = min(self.first_selec_pos[1], self.second_selec_pos[1])
        maxy = max(self.first_selec_pos[1], self.second_selec_pos[1])

        for i in range(minx, maxx + 1):
            for j in range(miny, maxy + 1):
                try: tile = self.matrix[j][i]
                except: continue
                if tile is None: continue
                if i < 0 or j < 0 or i >= self.levelsizex or j >= self.levelsizey: continue

                try: 
                    if i > 0: left = True if self.matrix[j][i - 1] is None else False
                    else: left = True
                except: left = True
                try: 
                    if i < self.levelsizex: right = True if self.matrix[j][i + 1] is None else False
                    else: right = True
                except: right = True
                try: 
                    if j > 0: up = True if self.matrix[j - 1][i] is None else False
                    else: up = True
                except: up = True
                try: 
                    if j < self.levelsizey: down = True if self.matrix[j + 1][i] is None else False
                    else: down = True
                except: down = True
                
                if left and up: newtile = "upleft"
                elif right and up: newtile = "upright"
                elif left and down: newtile = "downleft"
                elif right and down: newtile = "downright"

                elif left: newtile = "left"
                elif right: newtile = "right"
                elif up: newtile = "up"
                elif down: newtile = "down"

                else: newtile = "center"

                self.matrix[j][i] = newtile

    def update(self):
        self.zoom = self.tilesize / self.zoom_scroll.get_original_val()

        mscoord = self.cam_to_pos(self.mspos)
        msmatrix = self.matrix_pos(mscoord)

        collidetileset = self.tileset_chooser_rect.collidepoint(self.mspos)
        collidetiles = self.tile_chooser_rect.collidepoint(self.mspos)
        collidescroll = self.zoom_scroll.rect.collidepoint(self.mspos)
        is_scrolling = self.zoom_scroll.scrolling
        if not collidetileset and not collidetiles and not collidescroll and not is_scrolling:
            if not self.selectioning:
                if msmatrix[0] >= 0 and msmatrix[1] >= 0 and msmatrix[0] < self.levelsizex and msmatrix[1] < self.levelsizey:
                    if self.placing:
                        self.saved = False
                        self.ended_selec = False
                        try: self.matrix[msmatrix[1]][msmatrix[0]] = self.actual_block
                        except: pass
                    elif self.erasing:
                        self.saved = False
                        self.ended_selec = False
                        try: self.matrix[msmatrix[1]][msmatrix[0]] = None
                        except: pass
        
        pressed = pygame.key.get_pressed()
        
        if self.selectioning: 
            self.second_selec_pos = self.matrix_pos(self.cam_to_pos(self.mspos))
            self.visual_second_pos = self.cam_to_pos(self.mspos)

        if self.ended_selec:
            if pressed[pygame.K_r]:
                self.ended_selec = False
                self.saved = False
                self.rearrange()
            elif pressed[pygame.K_BACKSPACE]:
                self.ended_selec = False
                self.saved = False
                first_point = self.first_selec_pos
                second_point = self.second_selec_pos

                minx = min(first_point[0], second_point[0])
                miny = min(first_point[1], second_point[1])

                maxx = max(first_point[0], second_point[0])
                maxy = max(first_point[1], second_point[1])

                for i in range(minx, maxx + 1):
                    for j in range(miny, maxy + 1):
                        try: self.matrix[j][i] = None
                        except: continue
            elif pressed[pygame.K_f]:
                self.ended_selec = False
                self.saved = False
                self.fill_area(self.first_selec_pos, self.second_selec_pos, self.actual_block)
            elif pressed[pygame.K_RETURN]:
                self.ended_selec = False
                self.saved = False
                self.replace_area(self.first_selec_pos, self.second_selec_pos, self.actual_block)


        if pressed[pygame.K_BACKSPACE]: 
            try: self.matrix[msmatrix[1]][msmatrix[0]] = None
            except: pass
            self.saved = False
        
        if pressed[pygame.K_c]:
            try: self.actual_block = self.matrix[msmatrix[1]][msmatrix[0]]
            except: pass


        if pressed[pygame.K_q]: self.cam_offset.x -= self.cam_speed * self.dt
        if pressed[pygame.K_z]: self.cam_offset.y -= self.cam_speed * self.dt
        
        if pressed[pygame.K_s]: self.cam_offset.y += self.cam_speed * self.dt
        if pressed[pygame.K_d]: self.cam_offset.x += self.cam_speed * self.dt

        if pressed[pygame.K_t] and pressed[1073742051]: 
            self.matrix = deepcopy(self.saved_matrix)
            self.saved = True

        new_tilesize = int(self.zoom_scroll.get_var())
        if new_tilesize != self.tilesize:
            initial_pos = self.cam_offset
            old_tilesize = self.tilesize
            self.tilesize = new_tilesize
            multi = self.tilesize / old_tilesize
            self.cam_offset = pygame.Vector2(initial_pos.x * multi, initial_pos.y * multi)
        self.border_rect = pygame.Rect(0, 0, self.levelsizex * self.tilesize, self.levelsizey * self.tilesize)
   
    def fill_area(self, firstpos, secondpos, new_block):
        firstmatrixpos = firstpos
        secondmatrixpos = secondpos
        minx = int(min(firstmatrixpos[0], secondmatrixpos[0]))
        miny = int(min(firstmatrixpos[1], secondmatrixpos[1]))
        maxx = int(max(firstmatrixpos[0], secondmatrixpos[0]))
        maxy = int(max(firstmatrixpos[1], secondmatrixpos[1]))

        for i in range(minx, maxx + 1):
            for j in range(miny, maxy + 1):
                try: self.matrix[j][i] = new_block
                except: continue

    def replace_area(self, firstpos, secondpos, new_block):
        firstmatrixpos = firstpos
        secondmatrixpos = secondpos
        minx = int(min(firstmatrixpos[0], secondmatrixpos[0]))
        miny = int(min(firstmatrixpos[1], secondmatrixpos[1]))
        maxx = int(max(firstmatrixpos[0], secondmatrixpos[0]))
        maxy = int(max(firstmatrixpos[1], secondmatrixpos[1]))

        for i in range(minx, maxx + 1):
            for j in range(miny, maxy + 1):
                try: tile = self.matrix[j][i]
                except: continue
                if tile is None: continue

                self.matrix[j][i] = new_block

    def fill(self):
        mscoord = self.cam_to_pos(self.mspos)
        msmatrix = self.matrix_pos(mscoord)
        if msmatrix[0] < 0 or msmatrix[1] < 0 or msmatrix[0] >= self.levelsizex or msmatrix[1] >= self.levelsizey: return

        self.matrix = self.filler.floodFill(self.matrix, msmatrix[0], msmatrix[1], self.actual_block)
        self.saved = False

    def run(self):
        while self.running:
            self.mspos = pygame.mouse.get_pos()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                    elif event.key == pygame.K_f: 
                        if not self.ended_selec: self.fill()
                    elif event.key == pygame.K_RSHIFT: self.save()
                    
                    elif event.key == pygame.K_x:
                        self.selectioning = True
                        self.first_selec_pos = self.matrix_pos(self.cam_to_pos(self.mspos))
                        self.second_selec_pos = self.first_selec_pos
                        self.visual_first_pos = self.cam_to_pos(self.mspos)
                        self.visual_second_pos = self.visual_first_pos
                        self.first_pos_multiplier = deepcopy(self.tilesize)
                        self.ended_selec = False
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_x:
                        self.selectioning = False
                        self.second_selec_pos = self.matrix_pos(self.cam_to_pos(self.mspos))
                        self.visual_second_pos = self.cam_to_pos(self.mspos)
                        self.ended_selec = True

                elif event.type == pygame.MOUSEBUTTONDOWN: 
                    tileset_chooser = self.tileset_chooser_rect.collidepoint(self.mspos)
                    tile_chooser = self.tile_chooser_rect.collidepoint(self.mspos)
                    if not tileset_chooser and not tile_chooser:
                        if event.button == 1: self.placing = True
                        elif event.button == 3: self.erasing = True
                    elif tile_chooser:
                        if event.button == 1:
                            for i in self.block_choosing_rects.keys():
                                rect = self.block_choosing_rects[i]
                                if rect.collidepoint(self.mspos): 
                                    self.actual_block = i
                                    break
                                elif self.noneblock.collidepoint(self.mspos):
                                    self.actual_block = None
                                    break
                    elif tileset_chooser:
                        if event.button == 1:
                            for tileset in self.tileset_choosing_rects:
                                if tileset[3].collidepoint(self.mspos):
                                    self.actual_tileset = tileset[1]
                                    self.blocks = self.load_tileset()
                                    break
                                
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.placing = False
                    self.erasing = False
            
            
            self.update()
            self.zoom_scroll.update(events)
            
            self.screen.fill((0, 0, 0))
            self.refresh_screen()
            pygame.display.update()

            self.clock.tick(self.fps)
        
        return

    def save(self):
        file = f"level_{self.actual_map}.json"
        self.saved = True

        self.saved_matrix = deepcopy(self.matrix)

        data = {
            "level": self.matrix
        }
        with open(f"./levels/{file}", "w") as file:
            json.dump(data, file)
            file.close()



"""

X -> Selec
RETURN -> Replace
BACKSPACE -> Delete
RIGHTCLICK -> Delete
LEFTCLICK -> Place
F -> Fill
R -> Rearrange
C -> Copy the block (mouse)
T -> cmd z
RSHIFT -> Save

Move -> zqsd

"""




