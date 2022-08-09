import pygame




class DataBox:
    def __init__(self, pos, width, height, content) -> None:
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

        self.content = content
        self.screen = pygame.display.get_surface()

        self.color = "#ee6c4d"

        self.font = pygame.font.Font("Arial.ttf", 20)

        self.header = self.font.render("LEVEL FILES", True, "black")

        self.selectioned = 0

        self.reload()

    def reload(self):
        self.rects = []

        offset = 10
        self.header_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect.width, self.header.get_height() + offset * 2)
        offset_between_texts = 20
        text_rects_offset = 5
        offset = 0
        x = self.rect.left + offset_between_texts
        width = self.rect.width - (offset_between_texts * 2)
        for i, data in enumerate(self.content):
            textsurf = self.font.render(data["text"], True, (50, 50, 50))
            y = self.header_rect.bottom + (offset_between_texts * (i + 1)) + (offset / 2)
            height = textsurf.get_height() + text_rects_offset * 2
            rect = pygame.Rect(x, y, width, height)
            self.rects.append([rect, textsurf, data["value"]])
            offset += (rect.height + offset_between_texts)

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect, border_radius=5)
        pygame.draw.rect(self.screen, "white", self.rect, border_radius=5, width=4)

        offset = 10
        pygame.draw.rect(self.screen, "#3d5a80", self.header_rect, border_radius=5)
        self.screen.blit(self.header, (self.rect.centerx - self.header.get_width() / 2, self.rect.top + offset))

        for i, rect in enumerate(self.rects):
            color = "#98c1d9" if i != self.selectioned else "#668091"
            pygame.draw.rect(self.screen, color, rect[0], border_radius=3)
            x = rect[0].centerx - rect[1].get_width() / 2
            self.screen.blit(rect[1], (x, rect[0].top + 5))

    def get_selec(self): 
        try: return self.rects[self.selectioned][2]
        except: return None

    def check_click(self, mspos, click=False):
        clicked = False
        for i, rect in enumerate(self.rects):
            if rect[0].collidepoint(mspos):
                if click:
                    self.selectioned = i
                    clicked = True
                    break
        
        if not clicked and click: self.selectioned = None












