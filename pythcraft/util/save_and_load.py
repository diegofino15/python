import json, random

from pygame import Vector2
from sprites.block import Block



def save(world) -> bool:
    newchunks = {}
    for key in world.chunks.keys():
        realkey = f"{key[0]}:{key[1]}"
        newchunks.update({realkey: [[None for i in range(world.chunksize)] for j in range(world.chunksize)]})
        for i_row, row in enumerate(world.chunks[key]):
            for i_col, block in enumerate(row):
                if block is None: newchunks[realkey][i_row][i_col] = None
                else: newchunks[realkey][i_row][i_col] = block.id

    try:
        data = {
            "world": newchunks,
            "playerpos": [world.player.position.x, world.player.position.y],
            "playervel": [world.player.velocity.x, world.player.velocity.y],
            "tilesize": world.tilesize,
            "seed": world.seed
        }
        with open("./worlds/world.json", "w") as file:
            json.dump(data, file)
            file.close()
        
        return True
    except:
        return False


def load(world) -> dict:
    try:
        with open("./worlds/world.json", "r") as file:
            data = json.load(file)
            file.close()
        
        chunks = data["world"]
        
        newchunks = {}
        for key in chunks.keys():
            chunkpos = key.split(":")
            realkey = (int(chunkpos[0]), int(chunkpos[1]))
            newchunks.update({realkey: [[None for i in range(world.chunksize)] for j in range(world.chunksize)]})
            for i_row, row in enumerate(chunks[key]):
                for i_col, blockid in enumerate(row):
                    if blockid is None: continue

                    block = Block([i_col * world.tilesize, i_row * world.tilesize], blockid, world.tilesize)
                    newchunks[realkey][i_row][i_col] = block
        
        return {
            "world": newchunks,
            "playerpos": Vector2(data["playerpos"][0], data["playerpos"][1]),
            "playervel": Vector2(data["playervel"][0], data["playervel"][1]),
            "tilesize": data["tilesize"],
            "seed": data["seed"]
        }
    
    except:
        return None
    


            

