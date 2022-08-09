import pygame


from .camera import Camera
from .util.debug import debug



class Renderer:
    def __init__(self, world, width, height, title="Default py-engine title", tilesize=32) -> None:
        self.screenw = width
        self.screenh = height

        self.screen = pygame.display.set_mode((self.screenw, self.screenh))
        pygame.display.set_caption(title)

        self.world = world
        display = pygame.Surface((self.screenw, self.screenh))
        self.camera = Camera(self.world, display, tilesize)

    def render(self, fps):
        self.screen.fill((0, 0, 0))

        self.camera.display.fill((0, 0, 0))
        self.camera.render()
        self.screen.blit(self.camera.display, (0, 0))

        debug([f"FPS -> {fps}"], side="right", y="top", bg=True)

        pygame.display.update()









