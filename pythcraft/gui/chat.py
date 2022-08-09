import pygame, time


class Chat:
    def __init__(self, pos, width, height, delay, chatcolor, color) -> None:
        self.surf = pygame.Surface((width, height))
        self.surf.fill(color)
        self.surf.set_alpha(100)
        self.rect = self.surf.get_rect(topleft=(pos.x, pos.y))

        self.delay = delay
        self.chatcolor = chatcolor

        self.color = color
        
        self.messages = []
        self.last_message = -self.delay

        self.invisible = True

        self.screen = pygame.display.get_surface()

        pygame.font.init()
        self.font = pygame.font.Font(None, 32)
    
    def update(self, actual_time) -> None:
        if not self.invisible:
            if (self.last_message + self.delay) <= actual_time:
                self.invisible = True
        else:
            if (self.last_message + self.delay) >= actual_time:
                self.invisible = False
    
    def send_message(self, text) -> None: 
        self.messages.append(text)
        self.last_message = time.perf_counter()
    
    def draw(self) -> None:
        messages = []

        totaly = 0
        for text in self.messages:
            message = self.font.render(text, True, self.chatcolor)
            messages.append((totaly, message))
            totaly += message.get_height()

        self.surf.fill(self.color)
        if not self.invisible:
            for y, message in messages:
                posy = self.rect.height - totaly + y
                if posy > -message.get_height():
                    self.surf.blit(message, (5, posy - 5))
        
            pygame.draw.rect(self.screen, "grey", self.rect, width=3)
            self.screen.blit(self.surf, self.rect)







