import random
from pygame import Vector2
import pygame


class Body:
    DYNAMIC = 0
    STATIC = 1


class Keys:
    arrows = {
        "LEFT": pygame.K_LEFT,
        "RIGHT": pygame.K_RIGHT,
        "UP": pygame.K_UP,
        "DOWN": pygame.K_DOWN
    }
    default = {
        "LEFT": pygame.K_q,
        "RIGHT": pygame.K_d,
        "UP": pygame.K_z,
        "DOWN": pygame.K_s
    }


WIDTH, HEIGHT = 1280, 720
CENTER_SCREEN = Vector2(WIDTH // 2, HEIGHT // 2)

BLACK, WHITE, RED, BLUE, GREEN = "black", "white", "red", "blue", "green"


class Ball:
    def __init__(self, x, y, radius, color=BLACK, bodytype=Body.DYNAMIC) -> None:
        self.position = Vector2(x, y)
        self.radius = radius
        self.color = color
        self.bodytype = bodytype

        self.velocity = Vector2(0,0)

        self.last_pad_hit = 0

        self.max_y_vel = 300

    def draw(self, screen):
        x = self.position.x
        y = self.position.y

        if x - self.radius > WIDTH: return False
        if x + self.radius < 0: return False

        if y - self.radius > HEIGHT: return False
        if y + self.radius < 0: return False

        pygame.draw.circle(screen, self.color, (x, y), self.radius)
        return True
    
    def update(self, deltatime):
        self.position.x += self.velocity.x * deltatime

        if 0 < self.velocity.y > self.max_y_vel: self.velocity.y = self.max_y_vel
        elif self.max_y_vel > self.velocity.y < 0: self.velocity.y = -self.max_y_vel

        self.position.y += self.velocity.y * deltatime

    def handle_collisions(self, borders, secure, id=0):
        if id == 0:
            top = borders['top']
            bottom = borders['bottom']
            left = borders['left']
            right = borders['right']

            elasticity = borders['elasticity']

            if self.colliderect(top):
                self.velocity.y = -self.velocity.y * elasticity
                self.position.y = top.position.y + top.height / 2 + secure + self.radius       
            elif self.colliderect(bottom):
                self.velocity.y = -self.velocity.y * elasticity
                self.position.y = bottom.position.y - bottom.height / 2 - secure - self.radius
            if self.colliderect(left):
                self.velocity.x = -self.velocity.x * elasticity
                return False
            elif self.colliderect(right):
                self.velocity.x = -self.velocity.x * elasticity
                return False
            
            return True
        else:
            pad1 = borders[0]
            pad2 = borders[1]

            multiplier = 10
            increment = 10

            if self.colliderect(pad1):
                self.velocity.x = -self.velocity.x + increment
                self.position.x = pad1.position.x + pad1.width / 2 + secure + self.radius

                # Calculate the changement of angle
                posy = self.position.y
                posypad = pad1.position.y

                difference = posypad - posy + (random.randint(-8, 8) * multiplier)

                # La balle est en dessous du milieu du pad
                self.velocity.y -= (difference * multiplier)

                self.last_pad_hit = 1

            elif self.colliderect(pad2):
                self.velocity.x = -self.velocity.x - increment
                self.position.x = pad2.position.x - pad2.width / 2 - secure - self.radius

                # Calculate the changement of angle
                posy = self.position.y
                posypad = pad2.position.y

                difference = posypad - posy + (random.randint(-8, 8) * multiplier)

                # La balle est en dessous du milieu du pad
                self.velocity.y -= difference * multiplier

                self.last_pad_hit = 2
            
            return True
    
    def colliderect(self, collision):
        x = self.position.x - self.radius
        y = self.position.y - self.radius

        width = height = self.radius * 2

        x_col = collision.position.x - collision.width / 2
        y_col = collision.position.y - collision.height / 2

        width_col = collision.width
        height_col = collision.height

        if (x < (x_col + width_col) and x > x_col) or ((x + width) < (x_col + width_col) and (x + width) > x_col) or (x < x_col and (x + width) > (x_col + width_col)) or (x_col < x < (x + width) < (x_col + width_col)):
            if (y < (y_col + height_col) and y > y_col) or ((y + height) < (y_col + height_col) and (y + height) > y_col) or (y < y_col and (y + height) > (y_col + height_col)) or (y_col < y < (y + height) < (y_col + height_col)):
                return True
        
        return False


class Border:
    def __init__(self, x, y, width, height, color, bodytype=Body.STATIC) -> None:
        self.position = Vector2(x + width / 2, y + height / 2)
        self.width = width
        self.height = height
        self.color = color
        self.bodytype = bodytype
    
    def draw(self, screen):
        x = self.position.x - self.width / 2
        y = self.position.y - self.height / 2

        if (x + self.width) < 0: return False
        if x > WIDTH: return False

        if (y + self.height) < 0: return False
        if y > HEIGHT: return False

        pygame.draw.rect(screen, self.color, (x, y, self.width, self.height))
        return True


class Pad:
    def __init__(self, offset, offset_between_pad, size_borders, movespeed, width, height, number=0, color=GREEN) -> None:
        if number == 0: self.position = Vector2(offset + size_borders + offset_between_pad + width / 2, CENTER_SCREEN.y)
        else: self.position = Vector2(WIDTH - offset - size_borders - offset_between_pad - width / 2, CENTER_SCREEN.y)

        self.width = width
        self.height = height

        self.speed = movespeed

        self.offset = offset
        self.offset_between_pad = offset_between_pad
        self.size_borders = size_borders

        self.color = color
    
    def update(self):
        up_max = self.offset + self.size_borders + self.offset_between_pad + self.height / 2
        down_max = HEIGHT - self.offset - self.size_borders - self.offset_between_pad - self.height / 2

        if self.position.y < up_max: self.position.y = up_max
        elif self.position.y > down_max: self.position.y = down_max
    
    def move(self, pressed, keys, deltatime):
        up = pressed[keys['UP']]
        down = pressed[keys['DOWN']]

        if up: self.position.y -= self.speed * deltatime
        if down: self.position.y += self.speed * deltatime
    
    def draw(self, screen):
        x = self.position.x - self.width / 2
        y = self.position.y - self.height / 2

        pygame.draw.rect(screen, self.color, (x, y, self.width, self.height))


class Game:
    def __init__(self) -> None:
        pygame.init()

        self.fullscreen = True

        if self.fullscreen: self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        else: self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("PONG")

        self.clock = pygame.time.Clock()
        self.fps = 80
        self.deltatime = 1 / self.fps

        self.running = True

        self.keys_pad_1 = Keys.default
        self.keys_pad_2 = Keys.arrows

        self.init_objects()

        self.wait_time = 5
        self.begin_timer = self.wait_time * self.fps

        self.player1_points = 0
        self.player2_points = 0

        self.game_playing = True
        self.playing = True

        self.winner = 1

        pygame.font.init()

        self.font = pygame.font.SysFont(None, 50)
    
    def init_objects(self):
        # Borders
        self.offset = offset = 20
        self.size_sides = size_sides = 15

        # Pads
        offset_between_pad = 30
        width_pads = 40
        height_pads = 150
        speed_pads = 800


        # Initialize the pads
        self.pad1 = Pad(offset, offset_between_pad, size_sides, speed_pads, width_pads, height_pads, number=0, color=GREEN)
        self.pad2 = Pad(offset, offset_between_pad, size_sides, speed_pads, width_pads, height_pads, number=1, color=GREEN)

        self.pads = [self.pad1, self.pad2]

        # Initialize the ball
        self.ball = Ball(CENTER_SCREEN.x, CENTER_SCREEN.y, radius=20, color=GREEN)
        self.ball.velocity = Vector2(1000, 300)

        border_color = RED

        self.top = Border(offset, offset, WIDTH - offset * 2, size_sides, color=border_color)
        self.bottom = Border(offset, HEIGHT - offset - size_sides, WIDTH - offset * 2, size_sides, color=border_color)
        self.left = Border(offset, offset, size_sides, HEIGHT - offset * 2, color=border_color)
        self.right = Border(WIDTH - offset - size_sides, offset, size_sides, HEIGHT - offset * 2, color=border_color)

        self.borders = {
            'top': self.top,
            'bottom': self.bottom,
            
            'left': self.left,
            'right': self.right,

            'elasticity': 1
        }
    
    def update(self):
        if self.playing:
            # Restart the round
            if self.begin_timer == self.wait_time * self.fps:
                velx = random.randint(700, 1200)
                direction = random.randint(0, 1)
                vely = random.randint(-50, 50)

                if direction == 0: self.ball.velocity.x = velx
                else: self.ball.velocity.x = -velx

                self.ball.velocity.y = vely

                self.game_playing = True


            # Update the ball
            if self.game_playing:
                # Update the main ball
                if (self.wait_time * self.fps + 20) < self.begin_timer:
                    survive = self.ball.handle_collisions(self.borders, 2, id=0)
                else: survive = True
                if not survive:
                    winner = self.ball.last_pad_hit

                    if winner == 1: self.player1_points += 1
                    elif winner == 2: self.player2_points += 1
                
                    self.reset_game()

                self.ball.handle_collisions(self.pads, 2, id=1)
                self.ball.update(self.deltatime)
            
            
            # Draw all the sprites and get the player inputs
            self.ball.draw(self.screen)

            # Update the pads
            pressed = pygame.key.get_pressed()
            self.pad1.move(pressed, self.keys_pad_1, self.deltatime)
            self.pad2.move(pressed, self.keys_pad_2, self.deltatime)
            self.pad1.update()
            self.pad2.update()
            self.pad1.draw(self.screen)
            self.pad2.draw(self.screen)

            # Draw all the borders
            self.top.draw(self.screen)
            self.bottom.draw(self.screen)
            self.left.draw(self.screen)
            self.right.draw(self.screen)

            # Draw the player scores
            self.widgets()

            self.begin_timer += 1

            if self.player1_points >= 5:
                self.winner = 1
                self.restart()
            elif self.player2_points >= 5:
                self.winner = 2
                self.restart()

        # If the player is restarting the game
        else:
            self.end_widgets()

            mouse_pos = pygame.mouse.get_pos()

            if self.restart_button.collidepoint(mouse_pos):
                self.reset_game()
                self.player1_points = 0
                self.player2_points = 0

                self.playing = True
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        continue
            
            self.screen.fill(BLACK)
            
            self.update()
            
            pygame.display.update()

            self.clock.tick(self.fps)

            
        
        pygame.quit()

    def reset_game(self):
        self.ball.velocity = Vector2(0,0)
        self.ball.position = Vector2(WIDTH / 2, HEIGHT / 2)
        self.ball.last_pad_hit = 0

        self.begin_timer = 0
        self.game_playing = False

    def widgets(self):
        size_label = 50

        label1 = str(self.player1_points)
        self.screen.blit(self.font.render(label1, True, WHITE), (self.offset * 2 + self.size_sides, self.offset * 2 + self.size_sides))

        label2 = str(self.player2_points)
        self.screen.blit(self.font.render(label2, True, WHITE), (WIDTH - self.offset * 2 - self.size_sides - size_label, self.offset * 2 + self.size_sides))

    def restart(self):
        self.game_playing = False
        self.begin_timer = 0

        self.playing = False

    def end_widgets(self):
        restart_button_sizex = 300
        restart_button_sizey = 120
        self.restart_button = pygame.draw.rect(self.screen, RED, (CENTER_SCREEN.x - restart_button_sizex / 2, CENTER_SCREEN.y - restart_button_sizey / 2 + 200, restart_button_sizex, restart_button_sizey))

        label = self.font.render(f"Player {self.winner} won !", True, WHITE)
        self.screen.blit(label, (CENTER_SCREEN.x - 150, 150))

pong = Game()
pong.run()


# You can toggle fullscreen on and off


