import pygame, json



TEXTURES = {}
with open("./pyvoxel/tiles.json", "r") as file:
    infos = json.load(file)["tiles"]
    file.close()

for key in infos.keys():
    info = infos[key]

    texture = pygame.image.load(f"./assets/blocks/{info['texture']}")
    texture.set_colorkey((0, 0, 0))

    TEXTURES.update({key: texture})

def get_texture(tile_id): return TEXTURES[str(tile_id)]


class Tile:
    def __init__(self, world, abspos, id) -> None:
        self.world = world
        self.abspos = abspos
        self.id = id

        self.chunkaddr = (int(self.abspos[0] // world.chunksize), int(self.abspos[1] // world.chunksize))
        self.chunkpos = (int(self.abspos[0] - self.chunkaddr[0] * world.chunksize), int(self.abspos[1] - self.chunkaddr[1] * world.chunksize))

        self.collider = False
        self.rigid = False

        self.rect = pygame.Rect(self.abspos[0] * self.world.tilesize, self.abspos[1] * self.world.tilesize, self.world.tilesize, self.world.tilesize)

        self.texture = get_texture(self.id)
    
    def collide(self, entity):
        pass









