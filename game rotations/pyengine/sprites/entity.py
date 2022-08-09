import pygame, math



class Entity:
    def __init__(self, pos, size, texture_path, speed, world) -> None:
        self.position = pygame.Vector2(pos[0], pos[1])
        self.rect = pygame.Rect(self.position.x - size[0] / 2, self.position.y - size[1] / 2, size[0], size[1])

        self.texture = pygame.image.load(texture_path)
        self.texture = pygame.transform.scale(self.texture, size)
        self.texture.set_colorkey((0, 0, 0))

        self.speed = speed
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)

        self.false_vel = pygame.Vector2(0, 0)
        self.false_acc = pygame.Vector2(0, 0)

        self.rotation = 0

        self.world = world
    
    def update(self, dt) -> None:
        self.vertical_movement(dt)
        self.vertical_collisions()
        
        self.horizontal_movement(dt)
        self.horizontal_collisions()

        self.acceleration.x, self.acceleration.y = 0, 0
        self.false_acc.x, self.false_acc.y = 0, 0

    def vertical_movement(self, dt) -> None:
        self.acceleration.y += self.velocity.y * self.world.friction
        self.velocity.y += self.acceleration.y * dt
        self.position.y += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)
        self.rect.centery = self.position.y

        self.false_acc.y += self.false_vel.y * self.world.friction
        self.false_vel.y += self.false_acc.y * dt
    
    def horizontal_movement(self, dt) -> None:
        self.acceleration.x += self.velocity.x * self.world.friction
        self.velocity.x += self.acceleration.x * dt
        self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)
        self.rect.centerx = self.position.x

        self.false_acc.x += self.false_vel.x * self.world.friction
        self.false_vel.x += self.false_acc.x * dt

    def horizontal_collisions(self) -> None:
        for block in self.world.get_block_area(self.rect.topleft, self.rect.bottomright):
            if block is None or not block.collidable: continue
            if self.rect.colliderect(block.rect):
                block.collide(self)
                if block.rigid:
                    if self.velocity.x > 0:
                        self.velocity.x = 0
                        self.rect.right = block.rect.left
                        self.position.x = self.rect.centerx
                        return
                    elif self.velocity.x < 0:
                        self.velocity.x = 0
                        self.rect.left = block.rect.right
                        self.position.x = self.rect.centerx
                        return

    def vertical_collisions(self) -> None:
        for block in self.world.get_block_area(self.rect.topleft, self.rect.bottomright):
            if block is None or not block.collidable: continue

            if self.rect.colliderect(block.rect):
                block.collide(self)
                if block.rigid:
                    if self.velocity.y > 0:
                        self.velocity.y = 0
                        self.rect.bottom = block.rect.top
                        self.position.y = self.rect.centery
                        return
                    elif self.velocity.y < 0:
                        self.velocity.y = 0
                        self.rect.top = block.rect.bottom
                        self.position.y = self.rect.centery
                        return

    def draw(self, camera) -> None:
        x, y = camera.coord_to_pos((self.rect.width, self.rect.height))
        surf = pygame.transform.scale(self.texture, (int(x), int(y)))
        surf = pygame.transform.rotate(surf, self.rotation)
        surf.set_colorkey((0, 0, 0))

        pos = camera.coord_to_cam(self.position)
        drawpos = (pos[0] - surf.get_width() / 2, pos[1] - surf.get_height() / 2)
        camera.display.blit(surf, drawpos)


    def rotate_towards(self, point, need_return=False) -> None:
        A = (self.rect.centerx, self.rect.centery)
        C = (point[0], point[1])

        AB = C[0] - A[0]
        BC = C[1] - A[1]

        if AB == 0 or BC == 0: return

        AC = math.sqrt(AB ** 2 + BC ** 2)
        
        rot = math.acos(AB / AC) / math.pi * 180
        if self.rect.centery < point[1]: rot += (180 - rot) * 2

        if not need_return: self.rotation = rot
        else: return rot

    def rotate_towards_next_pos(self) -> None:
        next_pos = [self.position.x + self.false_vel.x, self.position.y + self.false_vel.y]
        self.rotate_towards(next_pos)


    def move(self, x, y, dt) -> None:
        self.acceleration.x = x
        self.acceleration.y = y

        if self.acceleration.x != 0 and self.acceleration.y != 0: self.acceleration = self.acceleration.normalize()
        self.acceleration.x *= self.speed * dt
        self.acceleration.y *= self.speed * dt

        self.false_acc.x, self.false_acc.y = self.acceleration.x, self.acceleration.y

    def moverot(self, dt, rot=None) -> None:
        AB, BC = rot_ratio(self.rotation) if rot is None else rot_ratio(rot)

        self.acceleration.x = AB * self.speed * dt
        self.acceleration.y = BC * self.speed * dt

        self.false_acc.x, self.false_acc.y = self.acceleration.x, self.acceleration.y

    def move_towards(self, target, dt) -> None:
        rot = self.rotate_towards(target, need_return=True)
        self.moverot(dt, rot)


def rot_ratio(angle) -> list:
    rot = angle / 180 * math.pi
    return [math.cos(rot), -math.sin(rot)]




