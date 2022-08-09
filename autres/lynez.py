import math
import pygame



class Ball:
    def __init__(self) -> None:
        self.pos = [250, 250]

        self.vel = pygame.Vector2(0, 0)

        self.radius = 30
    
    def update(self):
        self.pos[0] += self.vel.x
        self.pos[1] += self.vel.y
    
    def draw(self):
        pygame.draw.circle(screen, (200, 200, 200), self.pos, self.radius)



pygame.init()
screen = pygame.display.set_mode((500, 500))

ball = Ball()

running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
    
    screen.fill((0, 0, 0))
    ball.draw()
    pygame.display.update()

    clock.tick(60)
    ball.update()

pygame.quit()
















