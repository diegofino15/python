import pygame, os, json



BLOCKS_INFOS = json.load(open("./game_engine/sprites/blocks.json", "r"))["blocks"]




class BlockSelector:
    def __init__(self, instance, x, y, width, height, size=128, of=10) -> None:
        self.instance = instance

        self.blocks = []

        self.rect = pygame.Rect(x, y, width, height)

        currentx = of

        for key in BLOCKS_INFOS.keys():
            texture = BLOCKS_INFOS[key]['texture']

            if texture is not None:
                fullpath = f"./assets/blocks/{texture}"
                rect = pygame.Rect(currentx, of, size, size)
                img = pygame.transform.scale(pygame.image.load(fullpath), (size, size))
                self.blocks.append([rect, img])
                currentx += size + of
    
        self.selected = 0
        self.screen = pygame.display.get_surface()
    
    def update(self, *args):
        self.is_mouse_on = False
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(self.instance.msscreen):
            self.is_mouse_on = True
            for i, info in enumerate(self.blocks):
                blockrect, texture = info
                newrect = pygame.Rect(self.rect.left + blockrect.left, self.rect.top + blockrect.top, blockrect.width, blockrect.height)

                if newrect.collidepoint(self.instance.msscreen):
                    self.selected = i
                    return
    
    def draw(self):
        pygame.draw.rect(self.screen, "purple", self.rect)
        for i, info in enumerate(self.blocks):
            blockrect, texture = info
            newrect = pygame.Rect(self.rect.left + blockrect.left, self.rect.top + blockrect.top, blockrect.width, blockrect.height)
            self.screen.blit(texture, newrect)

            if i == self.selected:
                pygame.draw.rect(self.screen, "white", newrect, width=5, border_radius=2)










