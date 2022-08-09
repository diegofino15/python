import pygame

from pyengine.instance import Instance
from custom_sprites import Player



class Main(Instance):
    def __init__(self, screenw, screenh, title, filename="world-save", tilesize=32) -> None:
        super().__init__(screenw, screenh, title, tilesize)

        self.world.load(filename)

        size = int(self.world.tilesize // 1.1)
        self.player = Player([0, 0], [size, size], "./assets/sprites/sprite1.png", 100, self.world)
        self.world.entities.append(self.player)

        self.move_keys = {
            "left": pygame.K_q,
            "right": pygame.K_d,
            "up": pygame.K_z,
            "down": pygame.K_s
        }
    
    def update(self, dt) -> None:
        super().update(dt)

        self.handle_player(dt)

        self.camera.move_towards(self.player.position, dt, delay=0.1)

    def handle_player(self, dt) -> None:
        self.player.input(self.pressed, self.move_keys, dt)

        if self.pressed[pygame.K_SPACE]:
            self.player.rotate_towards(self.mscoord)
            self.player.moverot(dt)
        else: 
            self.player.rotate_towards_next_pos()
        
        if self.mouse_pressed[0]: self.player.fire()

    def run(self) -> None:
        super().run()
        self.world.save("world-save")

    def refresh(self) -> None:
        super().refresh()

        self.draw_text(f"MUNITIONS -> {self.player.weapon['munitions']}", (10, self.screenh - 40))




main = Main(1280, 720, "Python Game", tilesize=32)
main.run()





"""
ZQSD -> Move normally
Space -> Move in the direction of the mouse

"""




