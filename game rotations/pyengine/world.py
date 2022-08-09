import pickle

from .sprites.tile import Tile


class World:
    def __init__(self, friction, tilesize) -> None:
        self.tilesize = tilesize
        self.chunksize = 16

        self.sizex = 20
        self.sizey = 20

        self.chunks = {}

        self.entities = []
        self.friction = friction

        self.modified_blocks = {}
    
    def update(self, dt) -> None:
        for entity in self.entities:
            entity.update(dt)
    
    def load(self, filename) -> None:
        try:
            with open(f"./worlds/{filename}.pickle", "rb") as file:
                infos = pickle.load(file)["chunks"]
                file.close()
        except: infos = {}
        
        for key in infos.keys():
            chunkkey = (int(key.split(":")[0]), int(key.split(":")[1]))
            self.chunks.update({chunkkey: [[None for i in range(self.chunksize)] for j in range(self.chunksize)]})

            for i_row, row in enumerate(infos[key]):
                for i_col, tile_id in enumerate(row):
                    self.chunks[chunkkey][i_row][i_col] = Tile(i_col + chunkkey[0] * self.chunksize, i_row + chunkkey[1] * self.chunksize, tile_id, self)
    
    def save(self, filename) -> None:
        new_chunks = {}

        for key in self.chunks.keys():
            chunkkey = f"{key[0]}:{key[1]}"
            new_chunks.update({chunkkey: [[0 for i in range(self.chunksize)] for j in range(self.chunksize)]})

            for i_row, row in enumerate(self.chunks[key]):
                for i_col, tile in enumerate(row):
                    new_chunks[chunkkey][i_row][i_col] = tile.id

        data = {
            "chunks": new_chunks
        }
        with open(f"./worlds/{filename}.pickle", 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def get_block(self, coord) -> Tile:
        chunkx = int(coord[0] // self.chunksize)
        chunky = int(coord[1] // self.chunksize)

        posx = int(coord[0] - chunkx * self.chunksize)
        posy = int(coord[1] - chunky * self.chunksize)

        if (chunkx, chunky) in self.chunks.keys(): return self.chunks[(chunkx, chunky)][posy][posx]
    
    def set_block(self, coord, new_id) -> None:
        chunkx = int(coord[0] // self.chunksize)
        chunky = int(coord[1] // self.chunksize)

        posx = int(coord[0] - chunkx * self.chunksize)
        posy = int(coord[1] - chunky * self.chunksize)

        if (chunkx, chunky) in self.chunks.keys(): 
            self.chunks[(chunkx, chunky)][posy][posx].set(new_id)
            self.set_modified((chunkx, chunky), (posx, posy))
    
    def get_block_area(self, topleft, bottomright) -> list:
        minx = int(topleft[0] // self.tilesize // self.chunksize)
        maxx = int(bottomright[0] // self.tilesize // self.chunksize)
        miny = int(topleft[1] // self.tilesize // self.chunksize)
        maxy = int(bottomright[1] // self.tilesize // self.chunksize)

        chunkkeys = self.chunks.keys()
        
        tiles = []
        for i in range(minx, maxx + 1):
            for j in range(miny, maxy + 1):
                if (i, j) in chunkkeys:
                    for row in self.chunks[(i, j)]:
                        for tile in row:
                            tiles.append(tile)
        
        return tiles

    def set_modified(self, addr, pos) -> None:
        if addr in self.modified_blocks.keys(): self.modified_blocks[addr].append(pos)
        else: self.modified_blocks.update({addr: [pos]})

    def gen_chunk(self, addr) -> None:
        if not addr in self.chunks.keys(): self.chunks.update({addr: [[Tile(i + addr[0] * self.chunksize, j + addr[1] * self.chunksize, 0, self) for i in range(self.chunksize)] for j in range(self.chunksize)]})
    







