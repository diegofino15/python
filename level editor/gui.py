import pygame


class Scroll:
    def __init__(self, 
    pos, width, height, 
    init_var, min=0, max=100, 
    color=(71, 66, 80), bar_color="#6a6a6a", 
    outline_color="grey", outline_width=3, 
    bar_size=10, rounded=5, 
    axis="horizontal"
    ) -> None:
        self.variable = init_var
        self.min_var = min
        self.max_var = max

        self.axis = axis

        self.original_variable = init_var

        if self.variable < self.min_var: self.variable = self.min_var
        elif self.variable > self.max_var: self.variable = self.max_var

        self.scrolling = False

        self.color = color
        self.bar_color = bar_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.border = rounded

        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        if self.axis == "horizontal":
            self.real_rect = pygame.Rect(self.rect.left + bar_size / 2 + self.outline_width, self.rect.top, self.rect.width - bar_size - self.outline_width * 2, self.rect.height)
            self.ratio = self.real_rect.width / (self.max_var - self.min_var)
            self.bar_pos = self.real_rect.left + (self.variable - self.min_var) * self.ratio
            self.bar_rect = pygame.Rect(self.bar_pos - bar_size / 2, self.real_rect.top + self.outline_width, bar_size, self.real_rect.height - self.outline_width * 2)
            self.minx = self.real_rect.left
            self.maxx = self.real_rect.right
        elif self.axis == "vertical":
            self.real_rect = pygame.Rect(self.rect.left, self.rect.top + bar_size / 2 + self.outline_width, self.rect.width, self.rect.height - bar_size - self.outline_width * 2)
            self.ratio = self.real_rect.height / (self.max_var - self.min_var)
            self.bar_pos = self.real_rect.top + (self.variable - self.min_var) * self.ratio
            self.bar_rect = pygame.Rect(self.real_rect.left + self.outline_width, self.bar_pos - bar_size / 2, self.real_rect.width - self.outline_width * 2, bar_size)
            self.miny = self.real_rect.top
            self.maxy = self.real_rect.bottom

    def get_var(self): return self.variable
    def get_original_val(self): return self.original_variable

    def update(self, events):
        mspos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.bar_rect.collidepoint(mspos):
                    self.scrolling = True
                    if self.axis == "horizontal": self.diffx = mspos[0] - self.bar_pos
                    elif self.axis == "vertical": self.diffy = mspos[1] - self.bar_pos
            
            elif event.type == pygame.MOUSEBUTTONUP: self.scrolling = False
        
        if self.scrolling:
            if self.axis == "horizontal":
                target_x = mspos[0] - self.diffx
                self.bar_pos = target_x
            
                if self.bar_pos < self.minx: self.bar_pos = self.minx
                elif self.bar_pos > self.maxx: self.bar_pos = self.maxx

                self.variable = (self.bar_pos - self.real_rect.left) / self.ratio + self.min_var

                self.bar_rect.centerx = self.bar_pos

            elif self.axis == "vertical":
                target_y = mspos[1] - self.diffy
                self.bar_pos = target_y

                if self.bar_pos < self.miny: self.bar_pos = self.miny
                elif self.bar_pos > self.maxy: self.bar_pos = self.maxy

                self.variable = (self.bar_pos - self.real_rect.top) / self.ratio + self.min_var

                self.bar_rect.centery = self.bar_pos
            
            if self.variable > self.max_var: self.variable = self.max_var
            elif self.variable < self.min_var: self.variable = self.min_var
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=self.border)
        pygame.draw.rect(screen, self.outline_color, self.rect, width=self.outline_width)

        pygame.draw.rect(screen, self.bar_color, self.bar_rect)



class Button:
    def __init__(self,
    text, font,
    width, height,
    pos,
    elevation,
    click_action,
    color='#475F77',
    side_color='#354B5E',
    touch_color='#D74B4B',
    blocked=False,
    text_color='white',
    arguments=None
    ) -> None:
        # Core atttributes
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elevation = elevation
        self.original_y_pos = pos[1]

        # Top rectangle
        self.top_rect = pygame.Rect(pos, (width, height))
        self.top_color = color
        self.color = color

        # Bottom rectangle
        self.bottom_rect = pygame.Rect(pos, (width, elevation))
        self.bottom_color = side_color

        self.on_touch_color = touch_color

        self.font = font

        # Text
        self.text_surf = self.font.render(text, True, text_color)
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

        # Click logic
        self.click_action = click_action

        self.screen = pygame.display.get_surface()

        self.blocked = blocked
        self.text_color = text_color

        self.arguments = arguments

    def draw(self):
        # Elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elevation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elevation

        pygame.draw.rect(self.screen, self.bottom_color, self.bottom_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.top_color, self.top_rect, border_radius=8)
        self.screen.blit(self.text_surf, self.text_rect)
    
    def check_click(self, mouse_pos):
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = self.on_touch_color
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elevation = 0
                self.pressed = True
                return True
            else:
                self.dynamic_elevation = self.elevation
                if self.pressed:
                    self.click_action(self.arguments) if self.arguments is not None else self.click_action()
                    self.pressed = False
                    return True
        else:
            self.dynamic_elevation = self.elevation 
            self.top_color = self.color
            self.pressed = False
            return False




