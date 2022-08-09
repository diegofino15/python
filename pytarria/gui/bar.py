import pygame, time


class Bar:
    def __init__(self, pos, width, height, variable, max_variable, color, outline_color) -> None:
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.outline_rect = pygame.Rect(pos[0], pos[1], width, height)
        self.variable = variable
        self.max_variable = max_variable

        self.ratio = width / max_variable

        self.color = color
        self.outline_color = outline_color

        self.screen = pygame.display.get_surface()
    
    def update(self, new_variable):
        diff = time.perf_counter() - new_variable
        actual_width = diff * self.ratio

        if actual_width > self.outline_rect.width: actual_width = self.outline_rect.width

        pygame.draw.rect(self.screen, self.color, (self.rect.left, self.rect.top, actual_width, self.rect.height))
        pygame.draw.rect(self.screen, self.outline_color, self.outline_rect, width=4)







