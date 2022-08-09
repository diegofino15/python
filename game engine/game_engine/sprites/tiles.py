from game_engine.sprites.tile import Tile



class AIR(Tile):
    def __init__(self, pos, scene, id) -> None:
        super().__init__(pos, scene, id)

        self.visible = False



class TERRAIN(Tile):
    def __init__(self, pos, scene, id) -> None:
        super().__init__(pos, scene, id)



class WALL(Tile):
    def __init__(self, pos, scene, id) -> None:
        super().__init__(pos, scene, id)

        self.collider = True
        self.rigid = True


class BOUNCER(Tile):
    def __init__(self, pos, scene, id) -> None:
        super().__init__(pos, scene, id)

        self.collider = True
        self.rigid = True

    def collide(self, entity): 
        entity.velocity.x *= -1
        entity.velocity.y *= -1














