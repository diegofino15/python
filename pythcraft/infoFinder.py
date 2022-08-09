import pygame, json



class Menu:
    def __init__(self, pos, width, height) -> None:
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

        self.load()
        
        self.screen = pygame.display.get_surface()
        self.visible = True

        self.offset = 10
        self.box_size = 80

        self.name_rect = pygame.Rect(self.rect.left + self.offset, self.rect.top + self.offset, self.rect.width - self.offset * 2, self.box_size)
        self.texture_rect = pygame.Rect(self.name_rect.left, self.name_rect.bottom + self.offset, self.name_rect.width, self.box_size)
        self.tool_rect = pygame.Rect(self.texture_rect.left, self.texture_rect.bottom + self.offset, self.texture_rect.width / 2 - self.offset / 2, self.box_size)
        self.resistance_rect = pygame.Rect(self.tool_rect.right + self.offset, self.tool_rect.top, self.tool_rect.width, self.box_size)
        self.tools_to_break_rect = pygame.Rect(self.tool_rect.left, self.tool_rect.bottom + self.offset, self.texture_rect.width, self.box_size)
        self.drops_rect = pygame.Rect(self.tools_to_break_rect.left, self.tools_to_break_rect.bottom + self.offset, self.tool_rect.width, self.box_size)
        self.itemid_rect = pygame.Rect(self.drops_rect.right + self.offset, self.drops_rect.top, self.drops_rect.width, self.box_size)
        
        self.rects = [self.name_rect, self.texture_rect, self.tool_rect, self.resistance_rect, self.tools_to_break_rect, self.drops_rect, self.itemid_rect]

        self.infos = {
            "name": "",
            "tool": "",
            "resistance": 0,
            "tools-to-break": [],
            "drops": [],

            "texture": [0, 0],
            "itemid": 0
        }

        pygame.font.init()
        self.font = pygame.font.Font(None, 32)

    def load(self):
        with open("./assets/blocks.json", "r") as file:
            self.blocks = json.load(file)
            file.close()
        with open("./assets/items.json", "r") as file:
            self.items = json.load(file)
            file.close()

    def text(self, text, pos, color="white"):
        textsurf = self.font.render(str(text), True, color)
        self.screen.blit(textsurf, [pos[0] + self.offset, pos[1] + self.offset])

    def draw(self):
        if self.visible:
            pygame.draw.rect(self.screen, (50, 100, 100), self.rect)
            pygame.draw.rect(self.screen, "black", self.rect, width=4)
            for rect in self.rects:
                pygame.draw.rect(self.screen, "black", rect, width=2)
        
            self.text(self.infos["name"], self.name_rect.topleft)
            self.text(self.infos["tool"], self.tool_rect.topleft)
            self.text(self.infos["resistance"], self.resistance_rect.topleft)
            self.text(self.infos["tools-to-break"], self.tools_to_break_rect.topleft)
            self.text(self.infos["drops"], self.drops_rect.topleft)
            self.text(self.infos["texture"], self.texture_rect.topleft)
            self.text(self.infos["itemid"], self.itemid_rect.topleft)
    
    def find_selected(self, pos):
        for key in self.blocks.keys():
            block = self.blocks[key]

            if block["texture"][0] == pos[0] and block["texture"][1] == pos[1]:
                self.infos["name"] = block["name"]
                self.infos["tool"] = block["tool"]
                self.infos["resistance"] = block["resistance"]
                self.infos["tools-to-break"] = block["tools-to-break"]
                self.infos["drops"] = block["drops"]
                self.infos["texture"] = block["texture"]
                self.infos["itemid"] = block["itemid"]
            
                return
    
    def set(self, pos): self.find_selected(pos)



class InfoFinder:
    def __init__(self) -> None:
        self.screenw, self.screenh = 1280, 720

        self.screen = pygame.display.set_mode((self.screenw, self.screenh))
        pygame.display.set_caption("Block editor")

        self.running = True
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.tps = 20

        self.camera = [self.screenw // 2, self.screenh // 2]
        self.cam_speed = 20

        self.tilesize = 256
        
        self.tileset = pygame.image.load("./assets/tileset.png").convert()
        self.tileset = pygame.transform.scale(self.tileset, (4 * self.tilesize, 4 * self.tilesize))

        self.selected = [0, 0]

        self.menu = Menu([0, 0], 400, self.screenh)
        self.mouse_on_gui = False
    
    def pos_to_cam(self, pos): return [pos[0] - self.camera[0] + self.screenw / 2, pos[1] - self.camera[1] + self.screenh / 2]
    def cam_to_pos(self, pos): return [pos[0] + self.camera[0] - self.screenw / 2, pos[1] + self.camera[1] - self.screenh / 2]

    def line(self, p1, p2, color="red", width=1):
        pos1, pos2 = self.pos_to_cam(p1), self.pos_to_cam(p2)
        pygame.draw.line(self.screen, color, pos1, pos2, width=width)

    def run(self):
        while self.running:
            self.msscreen = pygame.mouse.get_pos()
            self.mspos = self.cam_to_pos(self.msscreen)
            self.pressed = pygame.key.get_pressed()

            self.dt = self.clock.tick(self.fps) * 0.001 * self.tps

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                    elif event.key == pygame.K_RSHIFT: self.menu.visible = not self.menu.visible
            
            self.refresh()
            self.update()
        
        pygame.quit()
    
    def refresh(self):
        self.screen.fill((0, 0, 0))

        pos = self.pos_to_cam([0, 0])
        self.screen.blit(self.tileset, pos)

        self.line([0, 0], [self.tilesize * 4, 0])
        self.line([self.tilesize * 4, 0], [self.tilesize * 4, self.tilesize * 4])
        self.line([self.tilesize * 4, self.tilesize * 4], [0, self.tilesize * 4])
        self.line([0, self.tilesize * 4], [0, 0])

        pos = self.pos_to_cam([self.selected[0] * self.tilesize, self.selected[1] * self.tilesize])
        pygame.draw.rect(self.screen, "white", (pos[0], pos[1], self.tilesize, self.tilesize), width=3)

        self.menu.draw()
        
        pygame.display.update()
    
    def update(self):
        if self.pressed[pygame.K_q]: self.camera[0] -= self.cam_speed * self.dt
        if self.pressed[pygame.K_d]: self.camera[0] += self.cam_speed * self.dt
        if self.pressed[pygame.K_z]: self.camera[1] -= self.cam_speed * self.dt
        if self.pressed[pygame.K_s]: self.camera[1] += self.cam_speed * self.dt

        self.mouse_on_gui = False
        if self.menu.rect.collidepoint(self.msscreen) and self.menu.visible: self.mouse_on_gui = True
        
        if not self.mouse_on_gui:
            if pygame.mouse.get_pressed()[0]:
                posx = self.mspos[0] // self.tilesize
                posy = self.mspos[1] // self.tilesize

                self.selected = [posx, posy]
                self.menu.set([posx * 16, posy * 16])



infoFinder = InfoFinder()
infoFinder.run()








