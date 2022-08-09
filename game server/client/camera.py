import pygame



class Camera:
    def __init__(self, screenw, screenh) -> None:
        self.position = [0, 0]
        self.target = [0, 0]

        self.tilesize = 64

        self.screenw, self.screenh = screenw, screenh

        self.delay = 0.3
        self.fps = 60
        self.ratio = self.fps * self.delay
        
        self.screen = pygame.display.get_surface()
    
    def pos_to_cam(self, pos): return [pos[0] - self.position[0] + self.screenw / 2, pos[1] - self.position[1] + self.screenh / 2]
    def cam_to_pos(self, pos): return [int(pos[0] + self.position[0] - self.screenw / 2), int(pos[1] + self.position[1] - self.screenh / 2)]

    def move(self, dt):
        disx = self.target[0] - self.position[0]
        disy = self.target[1] - self.position[1]

        pxlsx = disx / self.ratio
        pxlsy = disy / self.ratio

        self.position[0] += pxlsx * dt
        self.position[1] += pxlsy * dt
    
    def render(self, map):
        for i_row, row in enumerate(map):
            for i_col, tile in enumerate(row):
                if tile != 0:
                    pos = self.pos_to_cam([i_col * self.tilesize, i_row * self.tilesize])
                    pygame.draw.rect(self.screen, (255, 255, 0), (pos[0], pos[1], self.tilesize, self.tilesize))










