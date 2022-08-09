from game_engine.renderer.instance import Instance

from player import Player


class Game(Instance):
    def __init__(self, tilesize=8, size=20, file="world1") -> None:
        super().__init__(tilesize, size, file)

        self.player = Player([0, 0], [self.scene.tilesize * 5, self.scene.tilesize * 5], self.scene, "./assets/sprites/player", 100)
        self.scene.add_entity(self.player)
    
    def update(self):
        self.player.input(self.pressed)

        self.camera.smooth_follow(self.player.position, 0.1, self.dt)

        super().update()




game = Game()
game.run()


