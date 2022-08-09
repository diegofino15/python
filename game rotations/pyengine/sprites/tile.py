import pygame

from ..util.util import BLOCKS_INFOS



TEXTURES = {}
for key in BLOCKS_INFOS.keys(): TEXTURES.update({key: pygame.image.load(f"./assets/blocks/{BLOCKS_INFOS[key]['texture']}")})


def get_texture(block_id) -> pygame.Surface: return TEXTURES[str(block_id)]



class Tile:
    def __init__(self, x, y, id, world) -> None:
        self.pos = [x, y]
        self.world = world

        self.chunk_addr = [int(x // self.world.chunksize), int(y // self.world.chunksize)]
        self.chunk_pos = [int(self.pos[0] - self.chunk_addr[0] * self.world.chunksize), int(self.pos[1] - self.chunk_addr[1] * self.world.chunksize)]

        self.id = id

        self.rect = pygame.Rect(x * self.world.tilesize, y * self.world.tilesize, self.world.tilesize, self.world.tilesize)
        self.texture = get_texture(self.id)

        self.collidable = BLOCKS_INFOS[str(self.id)]["collidable"]
        self.rigid = BLOCKS_INFOS[str(self.id)]["rigid"]
        self.visible = BLOCKS_INFOS[str(self.id)]["visible"]
    
    def set(self, new_id) -> None: self.__init__(self.pos[0], self.pos[1], new_id, self.world)
    
    def collide(self, entity) -> None:
        pass












