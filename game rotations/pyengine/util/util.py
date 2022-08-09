import json


with open("./pyengine/util/BLOCKS.json", "r") as file:
    BLOCKS_INFOS = json.load(file)
    file.close()

