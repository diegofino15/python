import pygame, json


textures = {}
with open("./game_engine/sprites/blocks.json", "r") as file:
    infos = json.load(file)
    file.close()

for key in infos["blocks"].keys():
    info = infos["blocks"][key]
    texture = info['texture']

    if texture is not None: textures.update({key: pygame.image.load(f"./assets/blocks/{texture}")})
    else: textures.update({key: None})


def get_texture(id):
    return textures[str(id)]



class Tile:
    def __init__(self, pos, scene, id) -> None:
        self.position = pos
        self.scene = scene

        self.id = id

        self.rect = pygame.Rect(pos[0] * scene.tilesize, pos[1] * scene.tilesize, scene.tilesize, scene.tilesize)
        self.texture = get_texture(id)

        self.chunk_addr = (int(pos[0] // scene.chunksize), int(pos[1] // scene.chunksize))
        self.chunk_pos = (int(pos[0] - self.chunk_addr[0] * scene.chunksize), int(pos[1] - self.chunk_addr[1] * scene.chunksize))

        self.collider = False
        self.rigid = False

        self.visible = True
    
    def set(self, new_id):
        self.id = new_id
        self.texture = get_texture(new_id)

        self.scene.set_modified(self.chunk_addr, self.chunk_pos)
        self.scene.setblock(self.position, new_id)
    
    def collide(self, entity):
        pass













