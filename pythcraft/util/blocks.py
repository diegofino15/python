import pygame, json

tileset = pygame.image.load("./assets/tileset.png")
itemset = pygame.image.load("./assets/itemset.png")


with open("./assets/blocks.json", "r") as file:
    blocks = json.load(file)
    file.close()

with open("./assets/items.json", "r") as file:
    items = json.load(file)
    file.close()

def find_texture_pos(id) -> pygame.Surface: return blocks[str(id)]["texture"]

def get_texture(pos, size=16, file=tileset) -> pygame.Surface:
    image = file.subsurface(pos[0], pos[1], size, size)
    return image


