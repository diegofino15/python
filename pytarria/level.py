import json, noise, random


structures = {
    "house": [
        [4, 4, 4],
        [4, 0, 4],
        [4, 0, 4],
        [4, 0, 4],
        [4, 4, 4]
    ]
}



class Level:
    def __init__(self) -> None:
        self.width = 3
        self.height = 3

        self.world_file = "world"

        self.chunk_size = 16
        self.world, self.seed, self.playerpos, tilesize = self.load()
        self.init_tilesize = tilesize

        self.min_height = -256
        self.max_height = 256
        self.max_biome_height = 30
        self.min_biome_height = 10

        self.max_world_size = 128
        self.max_world_height = 16

        self.ratio = self.max_biome_height - self.min_biome_height

        self.block_breaking_times = {
            "0": 0,
            "1": .2,
            "2": .2,
            "3": 1,
            "4": 20
        }

        self.blocks = {
            "grass": 1,
            "dirt": 2,
            "stone": 3,
            "bedrock": 4
        }

        self.tools = {
            "pickaxe": 0
        }

        self.structures = [
            {
                "generated": False,
                "pos": [14, 2],
                "name": "house"
            }
        ]

        self.setup_structures()

    def setup_structures(self):
        self.blocks_to_place = []
        worldkeys = self.world.keys()
        for structure in self.structures:
            if not structure["generated"]:

                future_blocks = []

                generate = True
                structure["pos"][1] -= len(structures[structure["name"]])
                for i_row, row in enumerate(structures[structure["name"]]):
                    for i_col, tile in enumerate(row):
                        if tile == 0: continue
                        abs_x = structure["pos"][0] + i_col
                        abs_y = structure["pos"][1] + i_row

                        chunkpos = [int(abs_x // self.chunk_size), int(abs_y // self.chunk_size)]
                        addr = str(chunkpos[0]) + ":" + str(chunkpos[1])
                        x, y = abs_x - (chunkpos[0] * self.chunk_size), abs_y - (chunkpos[1] * self.chunk_size)
                        
                        if addr in worldkeys: 
                            generate = False
                            break
                        
                        future_blocks.append([addr, [x, y], tile])
                    
                    if not generate: break
                
                if generate:
                    self.blocks_to_place.extend(future_blocks)
    
    def add_structure(self, absx, absy):
        self.structures.append(
            {
                "generated": False,
                "pos": [absx, absy],
                "name": "house"
            }
        )

    def try_generate(self, chunkpos) -> None:
        chunk_address = str(chunkpos[0]) + ":" + str(chunkpos[1])
        if chunkpos[0] > self.max_world_size or chunkpos[0] < -self.max_world_size or chunkpos[1] < -self.max_world_height or chunkpos[1] > self.max_world_height: return
        if not chunk_address in self.world.keys():
            chunk = [[0 for i in range(self.chunk_size)] for j in range(self.chunk_size)]
            for x in range(self.chunk_size):
                target_x = chunkpos[0] * self.chunk_size + x
                height = noise.pnoise1(target_x * 0.02 + self.seed * 0.02, repeat=9999999)
                target_height = int(height * self.ratio)
                grass_size = random.randint(0, 2) + 3

                for y in range(self.chunk_size):
                    target_y = chunkpos[1] * self.chunk_size + y

                    diff = target_y - target_height

                    # Sky
                    if diff < 0: tile = 0
                    # Bottom of the world
                    elif target_y > -self.min_height: tile = 0
                    elif target_y == -self.min_height: tile = 4

                    elif diff == 0: 
                        tile = 1
                        #spawn_structure = random.randint(0, 20)
                        #if spawn_structure <= 5:
                        #self.add_structure(target_x, target_y)
                        #self.setup_structures()

                    elif diff <= grass_size: tile = 2
                    else: tile = 3
                    
                    chunk[y][x] = tile
            
            for addr, pos, block in self.blocks_to_place:
                if addr == chunk_address:
                    chunk[pos[1]][pos[0]] = block
            
            self.world.update({chunk_address: chunk})
    
    def save(self, playerpos, tilesize) -> None:
        data = {
            "world": self.world,
            "seed": self.seed,
            "player": playerpos,
            "zoom": tilesize
        }
        with open(f"./worlds/{self.world_file}.json", "w") as file:
            json.dump(data, file)
            file.close()

    def load(self) -> tuple:
        try:
            with open(f"./worlds/{self.world_file}.json", "r") as file:
                info = json.load(file)
                file.close()

            return [info["world"], info["seed"], info["player"], info["zoom"]]
        
        except:
            seed = random.randint(100000, 999999)
            print(f"Could not find a valable world, using seed {seed}")
            return [{}, seed, [1, 1], 32]

    def placeat(self, chunkpos, blockpos, what) -> bool:
        address = str(chunkpos[0]) + ":" + str(chunkpos[1])
        if address in self.world.keys():
            abs_x = chunkpos[0] * self.chunk_size + blockpos[0]
            abs_y = chunkpos[1] * self.chunk_size + blockpos[1]
            if abs_y >= -self.min_height: return False
            elif abs_y <= self.min_height: return False
            if self.world[address][blockpos[1]][blockpos[0]] == 0:
                self.world[address][blockpos[1]][blockpos[0]] = what
                return True
            return False
    
    def destroyat(self, chunkpos, blockpos):
        address = str(chunkpos[0]) + ":" + str(chunkpos[1])
        if address in self.world.keys():
            abs_y = chunkpos[1] * self.chunk_size + blockpos[1]
            if abs_y >= -self.min_height: return False
            elif abs_y <= self.min_height: return False
            if self.world[address][blockpos[1]][blockpos[0]] != 4:
                self.world[address][blockpos[1]][blockpos[0]] = 0
                return True
            return False




