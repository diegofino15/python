from .tile import Tile



class TERRAIN(Tile):
    def __init__(self, world, abspos, id) -> None:
        super().__init__(world, abspos, id)



class WALL(Tile):
    def __init__(self, world, abspos, id) -> None:
        super().__init__(world, abspos, id)

        self.collider = True
        self.rigid = True










