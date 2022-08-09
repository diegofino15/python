import pygame, os, sys
from gui import Button
from databox import DataBox
from level_editor import LevelEditor



class Main:
    def __init__(self) -> None:
        self.screen_w = 1280
        self.screen_h = 720

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.RESIZABLE)
        pygame.display.set_caption("Level editor")

        self.running = True
        self.framerate = 60
        self.clock = pygame.time.Clock()
        self.dt = 1 / self.framerate

        self.bg = "#293241"

        self.editor = LevelEditor()

        pygame.font.init()
        self.gui_font = pygame.font.Font("Arial.ttf", 32)
        
        width, height = 200, 60
        offset = 50
        x, y = self.screen_w / 2 - width / 2, self.screen_h - height / 2 - offset
        self.edit_button = Button("EDIT", self.gui_font, width, height, (x, y), 6, self.start)

        self.names = []
        for root, dirs, files in os.walk("./levels", topdown=False):
            for name in files:
                self.names.append([name, name[6]])
        
        self.names = sorted(self.names, key=lambda name: name[0])

        data = [{"text": levelname[0], "value": levelname[1]} for levelname in self.names]

        width, height = 500, 550
        x, y = self.screen_w / 2 - width / 2, 50
        self.databox = DataBox((x, y), width, height, data)

        self.create_level_button = Button("CREATE NEW", self.gui_font, width - 100, 60, (self.databox.rect.left + 50, self.databox.rect.bottom - 60 - 20), 6, self.create_level)

        offset = 10
        self.suppr_button = Button("SUPPR", self.gui_font, (self.databox.rect.width - self.edit_button.top_rect.width) / 2 - offset, self.edit_button.top_rect.height, (self.databox.rect.left, self.edit_button.top_rect.top), 6, self.suppr_level)

        self.quit_button = Button("QUIT", self.gui_font, (self.databox.rect.width - self.edit_button.top_rect.width) / 2 - offset, self.edit_button.top_rect.height, (self.edit_button.top_rect.right + offset, self.edit_button.top_rect.top), 6, self.quit)
    
    def recalculate_positions(self):
        width = 500
        x, y = self.screen_w / 2 - width / 2, 50
        self.databox.rect.topleft = (x, y)
        self.databox.reload()

        width, height = 200, 60
        offset = 50
        x = self.screen_w / 2 - width / 2
        self.edit_button = Button("EDIT", self.gui_font, width, height, (x, self.databox.rect.bottom + offset), 6, self.start)

        self.create_level_button = Button("CREATE NEW", self.gui_font, 400, 60, (self.databox.rect.left + 50, self.databox.rect.bottom - 60 - 20), 6, self.create_level)

        offset = 10
        self.suppr_button = Button("SUPPR", self.gui_font, (self.databox.rect.width - self.edit_button.top_rect.width) / 2 - offset, self.edit_button.top_rect.height, (self.edit_button.top_rect.right + offset, self.edit_button.top_rect.top), 6, self.suppr_level)

        self.quit_button = Button("QUIT", self.gui_font, (self.databox.rect.width - self.edit_button.top_rect.width) / 2 - offset, self.edit_button.top_rect.height, (self.databox.rect.left, self.edit_button.top_rect.top), 6, self.quit)
    
    def quit(self):
        pygame.quit()
        sys.exit()
    
    def suppr_level(self):
        level = self.databox.get_selec()
        if level is None: return

        path = f"./levels/level_{level}.json"

        if os.path.exists(path):
            os.remove(path)
            self.names.remove([f"level_{level}.json", level])
        
        self.names = sorted(self.names, key=lambda name: name[0])
        data = [{"text": levelname[0], "value": levelname[1]} for levelname in self.names]
        self.databox.content = data

        self.databox.reload()

        print(self.names)

    def create_level(self):
        for i in range(10):
            surpassed = False
            try: name = self.names[i][1]
            except: surpassed = True

            if surpassed or int(self.names[i][1]) != i:

                self.editor.set(i)
                self.editor.run()

                self.names.append([f"level_{i}.json", i])
                self.names = sorted(self.names, key=lambda name: name[0])
                data = [{"text": levelname[0], "value": levelname[1]} for levelname in self.names]
                self.databox.content = data

                self.databox.reload()

                break

    def start(self): 
        selec = self.databox.get_selec()
        if selec is None: return

        self.editor.set(selec)
        self.editor.run()

    def run(self):
        while self.running:
            self.events = pygame.event.get()
            self.mspos = pygame.mouse.get_pos()
            click = False
            for event in self.events:
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN: click = True

                elif event.type == pygame.VIDEORESIZE:
                    self.screen_w = event.w
                    self.screen_h = event.h
                    self.recalculate_positions()

            self.screen.fill(self.bg)
            self.refresh_screen()
            pygame.display.update()

            self.update(click)

            self.clock.tick(self.framerate)

            self.screen = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.RESIZABLE)
        
    def refresh_screen(self):
        self.edit_button.draw()
        self.databox.draw()
        self.create_level_button.draw()
        self.suppr_button.draw()
        self.quit_button.draw()

    def update(self, click):
        self.edit_button.check_click(self.mspos)
        self.create_level_button.check_click(self.mspos)
        self.suppr_button.check_click(self.mspos)
        self.quit_button.check_click(self.mspos)

        if not self.edit_button.top_rect.collidepoint(self.mspos) and not self.create_level_button.top_rect.collidepoint(self.mspos) and not self.suppr_button.top_rect.collidepoint(self.mspos):
            self.databox.check_click(self.mspos, click)


main = Main()
main.run()










