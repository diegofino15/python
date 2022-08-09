import random, noise
from sprites.block import Block
from pygame import Vector2
from util.save_and_load import save, load


class World:
    def __init__(self) -> None:
        self.entities = []

        self.tilesize = 256

        self.gravity = 1 / 16 * self.tilesize
        self.friction = -0.12

        self.chunks = {}
        self.worldsizeinchunks = 20
        self.worldsizeinchunksy = 5

        self.chunksize = 16

        self.min_height = -256
        self.max_height = 256
        self.max_biome_height = 30
        self.min_biome_height = 10
        self.max_world_size = 128
        self.max_world_height = 16
        self.ratio = self.max_biome_height - self.min_biome_height
    
    def load(self) -> dict: 
        loaded = load(self)
        if loaded is not None:
            self.chunks = loaded["world"]
            self.seed = loaded["seed"]

            return {
                "playerpos": loaded["playerpos"],
                "playervel": loaded["playervel"],
                "tilesize": loaded["tilesize"],
            }

        else:
            self.seed = random.randint(0, 999999)
            self.generate()
            self.chat.send_message("[WARNING] Generated a new world !")
            return False

    def save(self) -> bool: return save(self)
    
    def set_player(self, player) -> None: self.player = player
    def set_chat(self, chat) -> None: self.chat = chat

    def generate(self) -> None:
        for x_chunk in range(self.worldsizeinchunks):
            for y_chunk in range(self.worldsizeinchunksy):
                self.generate_chunk((x_chunk, y_chunk))
    
    def generate_chunk1(self, chunkpos) -> bool:
        if not chunkpos in self.chunks.keys():
            chunk = [[None for i in range(self.chunksize)] for j in range(self.chunksize)]

            for j in range(self.chunksize):
                posy = chunkpos[1] * self.chunksize + j
                for i in range(self.chunksize):
                    posx = chunkpos[0] * self.chunksize + i

                    blockid = self.find_blockid(posy)
                    if blockid is not None:
                        block = Block((posx * self.tilesize, posy * self.tilesize), blockid, self.tilesize)
                        chunk[j][i] = block
            
            self.chunks.update({chunkpos: chunk})
            return True
        return False

    def add_entity(self, entity) -> None: self.entities.append(entity)
    def remove_entity(self, entity) -> None: self.entities.remove(entity)

    def find_blockid(self, x, y, chunkpos) -> int:
        """if y < 0: return None
        elif y == 0: return 0
        elif y == 1 or y == 2 or y == 3: return 1
        elif y == 4: return 1 if random.randint(0, 1) == 0 else 2
        else: return 2 if random.randint(0, 1) == 0 else 3"""
  
        target_x = chunkpos[0] * self.chunksize + x
        height = noise.pnoise1(target_x * 0.02 + self.seed * 0.02, repeat=9999999)
        target_height = int(height * self.ratio)
        grass_size = random.randint(0, 2) + 3
        
        target_y = chunkpos[1] * self.chunksize + y
        diff = target_y - target_height
        
        # Sky
        if diff < 0: blockid = None
        # Bottom of the world
        elif target_y > -self.min_height: blockid = None
        elif target_y == -self.min_height: blockid = 6
        
        elif diff == 0: blockid = 0
        elif diff <= grass_size: blockid = 1
        else: blockid = random.randint(2, 3)

        return blockid

    def generate_chunk(self, chunkpos) -> None:
        if chunkpos[0] > self.max_world_size or chunkpos[0] < -self.max_world_size or chunkpos[1] < -self.max_world_height or chunkpos[1] > self.max_world_height: return
        if not chunkpos in self.chunks.keys():
            chunk = [[None for i in range(self.chunksize)] for j in range(self.chunksize)]
            for x in range(self.chunksize):
                for y in range(self.chunksize):
                    blockid = self.find_blockid(x, y, chunkpos)
                    if blockid is not None: block = Block(Vector2((x + chunkpos[0] * self.chunksize) * self.tilesize, (y + chunkpos[1] * self.chunksize) * self.tilesize), blockid, self.tilesize)
                    else: block = None
                    
                    chunk[y][x] = block
            
            self.chunks.update({chunkpos: chunk})


