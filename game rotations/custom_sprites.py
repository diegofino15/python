import math, time, pygame

from pyengine.sprites.entity import Entity, rot_ratio



class Player(Entity):
    def __init__(self, pos, size, texture_path, speed, world) -> None:
        super().__init__(pos, size, texture_path, speed, world)

        self.weapon = WEAPONS["0"]
        self.bullets = []
        self.last_shot = -self.weapon["delay-fire"]
    
    def update(self, dt) -> None:
        super().update(dt)

        for bullet in self.bullets:
            bullet.update(dt)
        self.bullets = [bullet for bullet in self.bullets if bullet.active]
    
    def input(self, pressed, keys, dt) -> None:
        x, y = 0, 0

        if pressed[keys["left"]]: x -= 1
        if pressed[keys["right"]]: x += 1
        if pressed[keys["up"]]: y -= 1
        if pressed[keys["down"]]: y += 1

        self.move(x, y, dt)

    def fire(self) -> None: 
        actual_time = time.perf_counter()
        if actual_time >= (self.last_shot + self.weapon["delay-fire"]):
            if self.weapon["munitions"] > 0:
                self.weapon["munitions"] -= 1
                self.last_shot = actual_time
                self.bullets.append(Bullet(self.position.x, self.position.y, self.rotation, self.weapon["bullet-speed"], self.weapon["bullet-distance"], self.world))

    def draw(self, camera) -> None:
        for bullet in self.bullets:
            drawpos = camera.coord_to_cam(bullet.pos)
            pygame.draw.circle(camera.display, (200, 200, 200), drawpos, 3)
        
        super().draw(camera)



WEAPONS = {
    "0": {
        "name": "glock",
        "type": "gun",
        "bullet-distance": 20,
        "bullet-speed": 500,
        "munitions": 1000,
        "delay-fire": 0.1
    }
}


class Bullet:
    def __init__(self, x, y, rot, speed, max_distance, world) -> None:
        self.pos = [x, y]
        self.initial_pos = [x, y]
        self.rot = rot

        self.active = True

        self.max_distance = max_distance
        self.world = world

        rotated_pos_ratio = rot_ratio(self.rot)
        self.speedx = rotated_pos_ratio[0] * speed
        self.speedy = rotated_pos_ratio[1] * speed

    def update(self, dt) -> None:
        self.pos[0] += self.speedx * dt
        self.pos[1] += self.speedy * dt

        disx = self.pos[0] - self.initial_pos[0]
        disy = self.pos[1] - self.initial_pos[1]
        dis = math.sqrt(disx ** 2 + disy ** 2)

        if dis >= (self.max_distance * self.world.tilesize): self.active = False
        
        self.check_collisions()
    
    def check_collisions(self) -> None:
        posx = int(self.pos[0] // self.world.tilesize)
        posy = int(self.pos[1] // self.world.tilesize)

        tile =  self.world.get_block((posx, posy))
        if tile is not None and tile.collidable and tile.rigid: self.active = False





