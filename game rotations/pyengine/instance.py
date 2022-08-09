import pygame

from .renderer.camera import Camera
from .world import World

class Instance:
    def __init__(self, 
    screenw, 
    screenh, 
    title,
    tilesize=32, 
    fps=60, 
    tps=20,
    friction=-.2,
    logic_tilesize=256) -> None:
        self.screenw = screenw
        self.screenh = screenh

        self.screen = pygame.display.set_mode((self.screenw, self.screenh))
        pygame.display.set_caption(title)

        self.running = True
        self.fps = fps
        self.tps = tps
        self.clock = pygame.time.Clock()

        self.world = World(friction, logic_tilesize)
        self.camera = Camera(self.screenw, self.screenh, self.world, tilesize)

        pygame.font.init()
        self.font = pygame.font.Font(None, 32)
    
    def refresh(self) -> None:
        self.camera.render()
        self.screen.blit(self.camera.display, (0, 0))

        self.draw_text(f"FPS -> {int(self.clock.get_fps())}", (10, 10))
    
    def draw_text(self, text, pos) -> None:
        surf = self.font.render(text, True, (200, 200, 200))
        self.screen.blit(surf, pos)

    def update(self, dt) -> None:
        self.world.update(dt)
        self.camera.update()

        for key in self.world.modified_blocks.keys(): 
            if not key in self.camera.need_to_modify: 
                self.camera.need_to_modify.append(key)

    def run(self) -> None:
        while self.running:
            self.msscreen = pygame.mouse.get_pos()
            self.mspos = self.camera.cam_to_pos(self.msscreen)
            self.mscoord = self.camera.pos_to_coord(self.mspos)

            self.pressed = pygame.key.get_pressed()
            self.mouse_pressed = pygame.mouse.get_pressed()

            self.dt = self.clock.tick(self.fps) * 0.001 * self.tps

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
            
            self.update(self.dt)

            self.screen.fill((0, 0, 0))
            self.refresh()
            pygame.display.update()
        
        pygame.quit()
        



