import pygame


tileset = pygame.image.load("ressources/tileset.png")
tileset.set_colorkey((0, 0, 0))

def get_texture(x, y, tileset=tileset) -> pygame.Surface: 
    return tileset.subsurface([x, y, 16, 16])


row = 1

blocks = {
    ("1", "grass"): get_texture(0, row*16),    # Grass
    ("2", "dirt"): get_texture(16, row*16),   # Dirt
    ("3", "stone"): get_texture(32, row*16),   # Stone
    ("4", "bedrock"): get_texture(48, row*16)    # Bedrock
}


items_tileset = pygame.image.load("ressources/item_tileset.png")
tileset.set_colorkey((0, 0, 0))

items = {
    "pickaxe": {
        "img": get_texture(0, 0, items_tileset),
        "tag": "tool"
    },
    "stone": {
        "img": get_texture(16, 0, items_tileset),
        "tag": "block"
    },
    "grass": {
        "img": get_texture(32, 0, items_tileset),
        "tag": "block"
    },
    "dirt": {
        "img": get_texture(48, 0, items_tileset),
        "tag": "block"
    },
}


