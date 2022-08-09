from pyvoxel.renderer import Renderer
from pyvoxel.world import World


import pygame



class Game:
    def __init__(self) -> None:
        self.world = World()
        self.world.load("world1")
        self.world.generate()

        self.renderer = Renderer(self.world, 1280, 720, "Test py-engine", tilesize=32)

        self.running = True
        self.fps = 60
        self.tps = 20
        self.clock = pygame.time.Clock()
        self.actual_fps = self.fps
    
    def run(self):
        while self.running:
            self.dt = self.clock.tick(self.fps) * 0.001 * self.tps
            self.actual_fps = int(self.clock.get_fps())
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
            
            self.renderer.render(self.actual_fps)
            self.renderer.camera.update()

            self.update(self.dt)
        
        pygame.quit()

    def update(self, dt):
        speed = 15 / self.renderer.camera.tilesize * self.world.tilesize
        if pygame.key.get_pressed()[pygame.K_d]: self.renderer.camera.position.x += speed * dt
        if pygame.key.get_pressed()[pygame.K_q]: self.renderer.camera.position.x -= speed * dt
        if pygame.key.get_pressed()[pygame.K_s]: self.renderer.camera.position.y += speed * dt
        if pygame.key.get_pressed()[pygame.K_z]: self.renderer.camera.position.y -= speed * dt

        if pygame.key.get_pressed()[pygame.K_UP]: 
            plus = 0.05 * self.renderer.camera.tilesize
            self.renderer.camera.tilesize += plus * self.dt
            self.renderer.camera.tilesize = max(5, min(self.renderer.camera.tilesize, 150))
            self.renderer.camera.update_tilesize()
        if pygame.key.get_pressed()[pygame.K_DOWN]: 
            plus = 0.05 * self.renderer.camera.tilesize
            self.renderer.camera.tilesize -= plus * self.dt
            self.renderer.camera.tilesize = max(5, min(self.renderer.camera.tilesize, 150))
            self.renderer.camera.update_tilesize()
        

        


test = Game()
test.run()





