from game_engine.renderer.scene import Scene
from game_engine.renderer.camera import Camera

from _thread import start_new_thread
import pygame
import time



class Instance:
    def __init__(self, tilesize=32, size=10, file="world1") -> None:
        self.screenw = 1280
        self.screenh = 720

        self.screen = pygame.display.set_mode((self.screenw, self.screenh))
        pygame.display.set_caption("Test game engine")

        self.running = True
        
        self.fps = 60
        self.tps = 20
        self.dt = 1
        self.clock = pygame.time.Clock()

        self.msscreen = [0, 0]
        self.mspos = [0, 0]
        self.mscoord = [0, 0]
        self.last_mscoord = [0, 0]
        self.actual_time = 0
        self.pressed = []

        self.scene = Scene(0, size)
        start_new_thread(self.scene.load, (file,))

        display = pygame.Surface((self.screenw, self.screenh))
        self.camera = Camera(display, self.scene, tilesize, self.fps)

        self.guis = []
        self.events = []

        self.on_gui = False

        pygame.font.init()
        self.big_font = pygame.font.Font(None, 50)

    def run(self):
        while not self.scene.loaded and self.running:
            self.screen.fill((0, 0, 0))

            text = "LOADING TERRAIN"
            surf = self.big_font.render(text, True, (200, 200, 200))
            width, height = surf.get_size()
            x = self.screenw / 2 - width / 2
            y = self.screenh / 2 - height / 2
            self.screen.blit(surf, (x, y))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False


        while self.running:
            self.msscreen = pygame.mouse.get_pos()
            self.mspos = self.camera.cam_to_pos(self.msscreen)
            self.last_mscoord = [self.mscoord[0], self.mscoord[1]]
            self.mscoord = self.camera.pos_to_coord(self.mspos)

            self.dt = self.clock.tick(self.fps) * 0.001 * self.tps

            self.actual_time = time.perf_counter()
            self.pressed = pygame.key.get_pressed()
            
            self.scene.modified = {}
            self.scene.chunks_generated = []

            self.events = pygame.event.get()
            for event in self.events:
                self.handle_events(event)
            
            self.screen.fill((0, 0, 0))
            self.tick()
            pygame.display.update()
    
    def update(self):
        self.scene.update(self.dt, self.actual_time)

        self.on_gui = False
        for gui in self.guis:
            gui.update(self.events)
            self.on_gui = self.on_gui or gui.is_mouse_on

    def refresh(self):
        self.camera.update(self.dt)
        self.camera.render()
        self.draw_borders()
        self.screen.blit(self.camera.display, (0, 0))

        for gui in self.guis:
            gui.draw()

    def draw_borders(self):
        minx, miny = self.camera.chunk_to_cam((-self.scene.sizex / 2, -self.scene.sizey / 2))
        maxx, maxy = self.camera.chunk_to_cam((self.scene.sizex / 2, self.scene.sizey / 2))

        pygame.draw.line(self.camera.display, "red", (minx, miny), (maxx, miny))
        pygame.draw.line(self.camera.display, "red", (maxx, miny), (maxx, maxy))
        pygame.draw.line(self.camera.display, "red", (maxx, maxy), (minx, maxy))
        pygame.draw.line(self.camera.display, "red", (minx, maxy), (minx, miny))

    def handle_events(self, event):
        if event.type == pygame.QUIT: self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.running = False

    def tick(self):
        self.update()
        self.refresh()

    def get_mouse_block_info(self):
        abspos = (self.mscoord[0] // self.scene.tilesize, self.mscoord[1] // self.scene.tilesize)
        addr = (int(self.mscoord[0] // self.scene.tilesize // self.scene.chunksize), int(self.mscoord[1] // self.scene.tilesize // self.scene.chunksize))
        pos = (int(abspos[0] - addr[0] * self.scene.chunksize), int(abspos[1] - addr[1] * self.scene.chunksize))

        return (abspos, addr, pos)

    def set_coord_block(self, x, y, id):
        abspos = (int(x // self.scene.tilesize), int(y // self.scene.tilesize))
        addr = (int(abspos[0] // self.scene.chunksize), int(abspos[1] // self.scene.chunksize))
        pos = (int(abspos[0] - addr[0] * self.scene.chunksize), int(abspos[1] - addr[1] * self.scene.chunksize))

        if addr in self.scene.chunks.keys():
            if self.is_block_different(abspos, id):
                self.scene.setblock(abspos, id)
                self.scene.set_modified(addr, pos)
        else:
            self.scene.gen_chunk(addr)
            self.set_coord_block(x, y, id)



