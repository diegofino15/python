import json

import game_engine.sprites.tiles as tiles


BLOCKS_INFOS = json.load(open("./game_engine/sprites/blocks.json", "r"))["blocks"]


class Scene:
    def __init__(self, id, size) -> None:
        self.id = id

        # Size used for positions and calculations
        self.tilesize = 256

        self.sizex = size
        self.sizey = size

        self.modified = {}
        self.chunks_generated = []

        self.chunksize = 16

        self.friction = -.15

        self.entities = []
        self.logic = True
    
    def add_entity(self, entity): self.entities.append(entity)
    def remove_entity(self, entity): self.entities.remove(entity)
    
    def load(self, filename):
        self.loaded = False
        self.chunks = {}

        try:
            with open(f"./game_engine/worlds/{filename}.json", "r") as file:
                infos = json.load(file)
                file.close()
        except:
            self.generate()
            self.loaded = True
            return
        
        chunks = infos["chunks"]
        self.chunks = {}

        for key in chunks.keys():
            chunk = chunks[key]

            chunk_key = (int(key.split(":")[0]), int(key.split(":")[1]))
            self.chunks.update({chunk_key: [[None for i in range(self.chunksize)] for j in range(self.chunksize)]})
            for i_row, row in enumerate(chunk):
                for i_col, tile_id in enumerate(row):

                    tile = self.get_tile(tile_id)

                    x = i_col + chunk_key[0] * self.chunksize
                    y = i_row + chunk_key[1] * self.chunksize

                    self.chunks[chunk_key][i_row][i_col] = tile((x, y), self, tile_id)
        
        self.loaded = True
    
    def save(self, filename):
        chunks = {}

        for key in self.chunks.keys():
            chunk = self.chunks[key]

            chunk_key = f"{key[0]}:{key[1]}"
            chunks.update({chunk_key: [[None for i in range(self.chunksize)] for j in range(self.chunksize)]})

            for i_row, row in enumerate(chunk):
                for i_col, tile in enumerate(row):

                    chunks[chunk_key][i_row][i_col] = tile.id
        
        data = {
            "chunks": chunks
        }
        
        with open(f"./game_engine/worlds/{filename}.json", "w") as file:
            json.dump(data, file)
            file.close()

    def generate(self):
        for i in range(self.sizex):
            for j in range(self.sizex):
                x = i - self.sizex / 2
                y = j - self.sizey / 2
                self.gen_chunk((int(x), int(y)))

    def get_tile(self, id): return eval(f"tiles.{BLOCKS_INFOS[str(id)]['tile']}")

    def update(self, dt, actual_time):
        if self.logic:
            for entity in self.entities:
                entity.update(dt, actual_time)

    def setblock(self, abspos, id):
        addr = (int(abspos[0] // self.chunksize), int(abspos[1] // self.chunksize))
        pos = (int(abspos[0] - addr[0] * self.chunksize), int(abspos[1] - addr[1] * self.chunksize))

        tile = self.get_tile(id)
        self.chunks[addr][pos[1]][pos[0]] = tile(abspos, self, id)

    def getblock(self, abspos):
        addr = (int(abspos[0] // self.chunksize), int(abspos[1] // self.chunksize))
        pos = (int(abspos[0] - addr[0] * self.chunksize), int(abspos[1] - addr[1] * self.chunksize))

        if addr in self.chunks.keys(): return self.chunks[addr][pos[1]][pos[0]]
        return None

    def gen_chunk(self, addr):
        if not addr in self.chunks.keys():
            new_chunk = [[tiles.AIR((i + addr[0] * self.chunksize, j + addr[1] * self.chunksize), self, -1) for i in range(self.chunksize)] for j in range(self.chunksize)]
            self.chunks.update({addr: new_chunk})
            self.chunks_generated.append(addr)

    def del_chunk(self, addr):
        if addr in self.chunks.keys():
            self.chunks.pop(addr)

    def set_modified(self, addr, pos): 
        if addr in self.modified.keys(): self.modified[addr].append(pos)
        else: self.modified.update({addr: [pos]})

    def coord_to_chunk(self, pos): return [int(pos[0] // self.tilesize // self.chunksize), int(pos[1] // self.tilesize // self.chunksize)]
    def chunk_to_coord(self, pos): return [pos[0] * self.chunksize * self.tilesize, pos[1] * self.chunksize * self.tilesize]

