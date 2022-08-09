import pygame


class Scroll:
    def __init__(self, 
    pos, width, height, 
    init_var, min=0, max=100, 
    color=(71, 66, 80), bar_color="#6a6a6a", 
    outline_color="grey", outline_width=3, 
    bar_size=10, rounded=5, 
    axis="horizontal",
    reverse=False,
    surf = None
    ) -> None:
        self.variable = init_var
        self.min_var = min
        self.max_var = max

        self.axis = axis

        self.screen = surf if surf is not None else pygame.display.get_surface()

        self.original_variable = init_var

        if self.variable < self.min_var: self.variable = self.min_var
        elif self.variable > self.max_var: self.variable = self.max_var

        self.scrolling = False

        self.color = color
        self.bar_color = bar_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.border = rounded

        self.reverse = reverse

        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        if self.axis == "horizontal":
            self.real_rect = pygame.Rect(self.rect.left + bar_size / 2 + self.outline_width, self.rect.top, self.rect.width - bar_size - self.outline_width * 2, self.rect.height)
            self.ratio = self.real_rect.width / (self.max_var - self.min_var)
            if not reverse: self.bar_pos = self.real_rect.left + (self.variable - self.min_var) * self.ratio
            else: self.bar_pos = self.real_rect.right - (self.variable - self.min_var) * self.ratio
            self.bar_rect = pygame.Rect(self.bar_pos - bar_size / 2, self.real_rect.top + self.outline_width, bar_size, self.real_rect.height - self.outline_width * 2)
            self.minx = self.real_rect.left
            self.maxx = self.real_rect.right
        elif self.axis == "vertical":
            self.real_rect = pygame.Rect(self.rect.left, self.rect.top + bar_size / 2 + self.outline_width, self.rect.width, self.rect.height - bar_size - self.outline_width * 2)
            self.ratio = self.real_rect.height / (self.max_var - self.min_var)
            if not reverse: self.bar_pos = self.real_rect.top + (self.variable - self.min_var) * self.ratio
            else: self.bar_pos = self.real_rect.bottom - (self.variable - self.min_var) * self.ratio
            self.bar_rect = pygame.Rect(self.real_rect.left + self.outline_width, self.bar_pos - bar_size / 2, self.real_rect.width - self.outline_width * 2, bar_size)
            self.miny = self.real_rect.top
            self.maxy = self.real_rect.bottom
        
        self.mouse_is_pressed = False

    def get_val(self): return self.variable
    def get_original_val(self): return self.original_variable

    def set(self, new_val):
        self.variable = new_val
        new_bar_pos = (self.variable - self.min_var) * self.ratio
        
        if self.axis == "horizontal": 
            if not self.reverse: self.bar_pos = new_bar_pos + self.real_rect.left
            else: self.bar_pos = self.real_rect.right - new_bar_pos
            self.bar_rect.centerx = self.bar_pos
        else: 
            if not self.reverse: self.bar_pos = new_bar_pos + self.real_rect.top
            else: self.bar_pos = self.real_rect.bottom - new_bar_pos
            self.bar_rect.centery = self.bar_pos

    def update(self, mspos):
        if pygame.mouse.get_pressed()[0]:
            if self.bar_rect.collidepoint(mspos) and not self.mouse_is_pressed:
                self.scrolling = True
                if self.axis == "horizontal": self.diffx = mspos[0] - self.bar_pos
                elif self.axis == "vertical": self.diffy = mspos[1] - self.bar_pos
                self.mouse_is_pressed = True
        else: 
            self.scrolling = False
            self.mouse_is_pressed = False
        
        if self.scrolling:
            if self.axis == "horizontal":
                target_x = mspos[0] - self.diffx
                self.bar_pos = target_x
            
                if self.bar_pos < self.minx: self.bar_pos = self.minx
                elif self.bar_pos > self.maxx: self.bar_pos = self.maxx

                if not self.reverse: self.variable = (self.bar_pos - self.real_rect.left) / self.ratio + self.min_var
                else: self.variable = (self.real_rect.right - self.bar_pos) / self.ratio + self.min_var

                self.bar_rect.centerx = self.bar_pos

            elif self.axis == "vertical":
                target_y = mspos[1] - self.diffy
                self.bar_pos = target_y

                if self.bar_pos < self.miny: self.bar_pos = self.miny
                elif self.bar_pos > self.maxy: self.bar_pos = self.maxy

                if not self.reverse: self.variable = (self.bar_pos - self.real_rect.top) / self.ratio + self.min_var
                else: self.variable = (self.real_rect.bottom - self.bar_pos) / self.ratio + self.min_var

                self.bar_rect.centery = self.bar_pos
            
            if self.variable > self.max_var: self.variable = self.max_var
            elif self.variable < self.min_var: self.variable = self.min_var
    
    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect, border_radius=self.border)
        pygame.draw.rect(self.screen, self.outline_color, self.rect, width=self.outline_width)

        pygame.draw.rect(self.screen, self.bar_color, self.bar_rect)








