import json, random


import pyvoxel.tiles as tiles



BLOCKS_INFOS = json.load(open("./pyvoxel/tiles.json", "r"))["tiles"]



class World:
    def __init__(self, tilesize=256, chunksize=16) -> None:
        self.tilesize = tilesize
        self.chunksize = chunksize

        self.chunks = {}

        self.entities = []
    
    def load(self, filename):
        self.chunks = {}

        with open(f"./worlds/{filename}.json", "r") as file:
            infos = json.load(file)
            file.close()
        
        chunks = infos["chunks"]

        for key in chunks.keys():
            chunk = chunks[key]

            chunkkey = (int(key.split(":")[0]), int(key.split(":")[1]))

            self.chunks.update({chunkkey: [[None for i in range(self.chunksize)] for j in range(self.chunksize)]})

            for i_row, row in enumerate(chunk):
                for i_col, tile_id in enumerate(row):
                    tile = self.get_tile(tile_id)

                    abspos = (i_col + chunkkey[0] * self.chunksize, i_row + chunkkey[1] * self.chunksize)
                    self.chunks[chunkkey][i_row][i_col] = tile(self, abspos, tile_id)
    
    def generate(self):
        for i in range(5):
            for j in range(5):
                self.gen_chunk((i, j))
                self.gen_chunk((-i, j))
                self.gen_chunk((i, -j))
                self.gen_chunk((-i, -j))
    
    def gen_chunk(self, addr):
        if addr not in self.chunks.keys():
            self.chunks.update({addr: [[None for i in range(self.chunksize)] for j in range(self.chunksize)]})
            for i in range(self.chunksize):
                for j in range(self.chunksize):
                    absx = i + addr[0] * self.chunksize
                    absy = j + addr[1] * self.chunksize

                    id = random.randint(0, 1)
                    tile = self.get_tile(id)
                    self.chunks[addr][j][i] = tile(self, (absx, absy), id)
            
            print(f"Generated chunk : {addr}")
    
    def get_tile(self, tile_id): return eval(f"tiles.{BLOCKS_INFOS[str(tile_id)]['type']}")

    def coord_to_chunk(self, pos): return [pos[0] // self.tilesize // self.chunksize, pos[1] // self.tilesize // self.chunksize]
    def chunk_to_coord(self, pos): return [pos[0] * self.chunksize * self.tilesize, pos[1] * self.chunksize * self.tilesize]





