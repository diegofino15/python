from game_engine.renderer.instance import Instance
from game_engine.renderer.debug import debug

from ui import BlockSelector

import pygame, queue


class Editor(Instance):
    def __init__(self) -> None:
        super().__init__(tilesize=2, size=20, file="world1")
        self.scene.logic = False

        self.cam_speed = 15 / self.camera.tilesize * self.scene.tilesize
        
        self.filler = Filler(self.scene)
        self.actual_block = 0

        size = 64
        height = size + 20
        self.blockSelector = BlockSelector(self, 0, self.screenh - height, self.screenw, height, size=size)
        self.guis.append(self.blockSelector)

    def is_block_different(self, abspos, new_block):
        actual_block = self.scene.getblock(abspos)
        if actual_block is not None and new_block != actual_block.id: return True
        return False
    
    def set_mouse_block(self, id):
        x1, y1 = self.last_mscoord
        x2, y2 = self.mscoord

        disx = x2 - x1
        disy = y2 - y1
        
        points = int(max(abs(disx), abs(disy)) / 10)

        for i in range(points):
            x = disx / points * i + x1
            y = disy / points * i + y1

            self.set_coord_block(x, y, id)
        
        self.set_coord_block(x2, y2, id)
    
    def update(self):
        if self.pressed[pygame.K_q]: self.camera.world_position.x -= self.cam_speed * self.dt
        if self.pressed[pygame.K_d]: self.camera.world_position.x += self.cam_speed * self.dt
        if self.pressed[pygame.K_z]: self.camera.world_position.y -= self.cam_speed * self.dt
        if self.pressed[pygame.K_s]: self.camera.world_position.y += self.cam_speed * self.dt
        if self.pressed[pygame.K_RSHIFT]: self.camera.smooth_follow(self.mscoord, 1, self.dt)
        
        self.on_gui = False
        for gui in self.guis:
            gui.update(self.events)
            self.on_gui = self.on_gui or gui.is_mouse_on

        if pygame.mouse.get_pressed()[0] and not self.on_gui: self.set_mouse_block(self.actual_block)
        elif pygame.mouse.get_pressed()[2] and not self.on_gui: self.set_mouse_block(-1)

        self.scene.update(self.dt, self.actual_time)

        self.actual_block = self.blockSelector.selected

        for chunk in self.scene.chunks_generated: self.camera.chunks_to_generate.append(chunk)
        for key in self.scene.modified.keys():
            for pos in self.scene.modified[key]:
                if key in self.camera.chunks_to_modify.keys(): self.camera.chunks_to_modify[key].append(pos)
                else: self.camera.chunks_to_modify.update({key: [pos]})
    
    def run(self):
        super().run()
        self.scene.save("world1")
    
    def refresh(self):
        self.camera.update(self.dt)
        self.camera.render()
        self.draw_borders()
        pygame.draw.circle(self.camera.display, "red", self.camera.coord_to_cam((0, 0)), 10)
        self.screen.blit(self.camera.display, (0, 0))
        self.draw_mouse()

        debug([f"FPS -> {int(self.clock.get_fps())}"], side="right", y="top")

        abspos = (int(self.mscoord[0] // self.scene.tilesize), int(self.mscoord[1] // self.scene.tilesize))
        addr = (int(abspos[0] // self.scene.chunksize), int(abspos[1] // self.scene.chunksize))
        pos = (int(abspos[0] - addr[0] * self.scene.chunksize), int(abspos[1] - addr[1] * self.scene.chunksize))

        debug([f"CHUNK : {addr}", f"POS : {pos}"], side="left", y="top")

        for gui in self.guis:
            gui.draw()

    def draw_mouse(self):
        drawpos = self.camera.chunk_to_cam(self.camera.coord_to_chunk(self.mscoord))
        size = self.camera.tilesize * self.scene.chunksize
        pygame.draw.rect(self.screen, "yellow", (drawpos[0], drawpos[1], size, size), width=3, border_radius=3)

        pos = (self.mscoord[0] // self.scene.tilesize * self.scene.tilesize, self.mscoord[1] // self.scene.tilesize * self.scene.tilesize)
        drawpos = self.camera.coord_to_cam(pos)
        pygame.draw.rect(self.screen, "yellow", (drawpos[0], drawpos[1], self.camera.tilesize, self.camera.tilesize), width=2, border_radius=2)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                abspos, addr, pos = self.get_mouse_block_info()
                tile = self.scene.getblock(abspos)
                if tile is not None: self.filler.floodFill(abspos, tile.id, self.actual_block)
        
        super().handle_events(event)


class Filler:
    def __init__(self, scene) -> None:
        self.scene = scene
        self.chunks = scene.chunks

        self.queue = queue.Queue()
    
    def get_pos(self, abspos):
        chunkpos = (int(abspos[0] // self.scene.chunksize), int(abspos[1] // self.scene.chunksize))
        pos = (int(abspos[0] - chunkpos[0] * self.scene.chunksize), int(abspos[1] - chunkpos[1] * self.scene.chunksize))

        return (chunkpos, pos)

    def floodFill(self, abspos, initial, new_data):
        chunkskeys = self.scene.chunks.keys()
        self.queue.put(self.get_pos(abspos))
        while not self.queue.empty():
            current_addr, current_pos = self.queue.get()
            current_abspos = (current_pos[0] + current_addr[0] * self.scene.chunksize, current_pos[1] + current_addr[1] * self.scene.chunksize)

            if current_addr in chunkskeys:
                if self.scene.getblock(current_abspos).id == new_data: continue

                self.scene.setblock(current_abspos, new_data)
                self.scene.set_modified(current_addr, current_pos)

                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_abspos = (current_abspos[0] + i, current_abspos[1] + j)
                    addr, pos = self.get_pos(new_abspos)

                    if addr in chunkskeys:
                        if self.scene.getblock(new_abspos).id != initial: continue
                        self.queue.put((addr, pos))



editor = Editor()
editor.run()



