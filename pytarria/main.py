# Essentials
import pygame, sys, time, math
from pygame.locals import *

# For smooth generation
from _thread import start_new_thread
from level import Level

# GUI
from gui.scroll import Scroll
from gui.debug import debug
from gui.inventory import Inventory

# Game components
from player import Player
from camera import Camera

# Init all the pygame stuff
pygame.init()
pygame.display.init()
pygame.font.init()


def r(x) -> float: return round(x * 10) / 10



class Main:
    def __init__(self) -> None:
        self.screen_size = (1280, 720)
        self.screen_w, self.screen_h = self.screen_size
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("PYTARRIA")

        self.fps = 60
        self.target_fps = 60
        self.clock = pygame.time.Clock()

        self.running = True

        self.level = Level()
        self.camera = Camera(self.level, self)

        self.font = pygame.font.Font(None, 32)

        offset = 20
        self.zoom_scroll = Scroll((offset, offset), 200, 30, 32, min=8, max=128, bar_size=50)

        try: x = self.camera.tilesize / self.level.playerpos[0]
        except: x = 0
        try: y = self.camera.tilesize / self.level.playerpos[1]
        except: y = 0
        
        self.player = Player((x, y), 25, 50, .35, -.12, .5, 8, self.camera.tilesize, reach=200)
        self.player.position.x, self.player.position.y = x, y
        self.camera.offset = self.player.position

        self.breaking_block = False
        self.time_breaking_block = 0
        self.time_remaining = 0
        self.block_breaking_time = 0
        self.block_breaking = {
            "abs": [0, 0],
            "begin": 0,
            "type": 1
        }

        self.pickaxe = {
            "strenght": 500
        }

        self.dt = 1
        self.mspos = pygame.mouse.get_pos()
        self.mscoord = self.camera.cam_to_pos(self.mspos)
        self.actual_time = 0

        slotsize = 40
        offset = 10
        self.inventory = Inventory((offset, self.screen_h - slotsize - offset*3), 10, slotsize, offset, self.level)

        self.zoom_scroll.set(self.level.init_tilesize+1)
        self.adjust_cam()
        
        start_new_thread(self.auto_generate, ())
    
    def get_world_pos(self, coord) -> list:
        chunk_coord = self.camera.pos_to_chunk(coord)
        offsetx = (coord[0] // self.camera.tilesize) - (chunk_coord[0] * self.level.chunk_size)
        offsety = (coord[1] // self.camera.tilesize) - (chunk_coord[1] * self.level.chunk_size)
        address = str(chunk_coord[0]) + ":" + str(chunk_coord[1])
        position = [int(offsetx), int(offsety)]
        abs_position = [int(coord[0] // self.camera.tilesize), int(coord[1] // self.camera.tilesize)]
        return [address, position, chunk_coord, abs_position]

    def get_cam_visible(self) -> list:
        topleft = self.get_world_pos(self.camera.cam_to_pos(self.camera.rect.topleft))
        bottomright = self.get_world_pos(self.camera.cam_to_pos(self.camera.rect.bottomright))

        chunks = []
        workdkeys = self.level.world.keys()
        for i in range(topleft[2][0], bottomright[2][0] + 1):
            for j in range(topleft[2][1], bottomright[2][1] + 1):
                address = str(i) + ":" + str(j)
                if address in workdkeys:
                    chunks.append([[i, j], self.level.world[address]])
        
        return chunks

    def refresh_screen(self) -> None:
        self.camera.render(self.screen, self.get_cam_visible())
        self.player.draw(self.screen, self.camera)

        keys = self.level.world.keys()
        label2 = ""
        for i, key in enumerate(keys):
            if key == self.mouse_info[0]:
                label2 = f"Number : {i}"
                break
        
        debug([f"Mouse chunkpos : {self.mouse_info[0]}", label2], font=self.font, side="right", y="bottom")
        
        #pos = self.camera.pos_to_cam(self.player.rect.center)
        #pygame.draw.circle(self.screen, "red", pos, self.player.reach, width=3)

        x, y = self.camera.pos_to_cam((self.mouse_info[2][0] * self.level.chunk_size * self.camera.tilesize, self.mouse_info[2][1] * self.level.chunk_size * self.camera.tilesize))
        pygame.draw.rect(self.screen, "orange", (x, y, self.level.chunk_size * self.camera.tilesize, self.level.chunk_size * self.camera.tilesize), width=3)

        if self.mouse_info[0] in self.level.world.keys():
            if self.level.world[self.mouse_info[0]][self.mouse_info[1][1]][self.mouse_info[1][0]] != 0:
                pos = (self.mscoord[0] // self.camera.tilesize * self.camera.tilesize, self.mscoord[1] // self.camera.tilesize * self.camera.tilesize)
                x, y = self.camera.pos_to_cam(pos)
                pygame.draw.rect(self.screen, "white", (x, y, self.camera.tilesize, self.camera.tilesize), width=3)

    def auto_generate(self) -> None:
        clock = pygame.time.Clock()
        while self.running:
            _, _, chpos1, _ =  self.get_world_pos(self.camera.cam_to_pos(self.camera.rect.topleft))
            _, _, chpos2, _ =  self.get_world_pos(self.camera.cam_to_pos(self.camera.rect.bottomright))
            
            for i in range(chpos1[0], chpos2[0] + 1):
                for j in range(chpos1[1], chpos2[1] + 1):
                    pos = [i, j]
                    self.level.try_generate(pos)
            
            clock.tick(2)

    def widgets(self, fps) -> None:
        label1 = f"FPS -> {int(fps)}"
        debug([label1], font=self.font, side="right", y="top", bg=True, color="white")

        self.zoom_scroll.draw()
        self.inventory.draw(self.screen)

    def create_collisions(self, position) -> list:
        coord = [position[0] // self.camera.tilesize, position[1] // self.camera.tilesize]
        chunkpos = [int(coord[0] // self.level.chunk_size), int(coord[1] // self.level.chunk_size)]
        offset = [chunkpos[0] * self.level.chunk_size * self.camera.tilesize, chunkpos[1] * self.level.chunk_size * self.camera.tilesize]
        addr = str(chunkpos[0]) + ":" + str(chunkpos[1])
        if addr in self.level.world.keys(): chunk = self.level.world[addr]
        else: return []

        cols = []
        for i_row, row in enumerate(chunk):
            for i_col, tile in enumerate(row):
                if tile == 0: continue

                x = i_col * self.camera.tilesize + offset[0]
                y = i_row * self.camera.tilesize + offset[1]

                rect = pygame.Rect(x, y, self.camera.tilesize, self.camera.tilesize)

                cols.append(rect)

        return cols
    
    def handle_player_collide(self, dt) -> None:
        of = 10
        collisionslist1 = self.create_collisions([self.player.position.x - of, self.player.position.y + of])
        collisionslist2 = self.create_collisions([self.player.position.x - of, self.player.position.y - self.player.rect.height - of])
        collisionslist3 = self.create_collisions([self.player.position.x + self.player.rect.width + of, self.player.position.y - self.player.rect.height - of])
        collisionslist4 = self.create_collisions([self.player.position.x + self.player.rect.width + of, self.player.position.y + of])
        
        collisionslist = collisionslist1
        for tile in collisionslist2:
            if not tile in collisionslist: collisionslist.append(tile)
        for tile in collisionslist3:
            if not tile in collisionslist: collisionslist.append(tile)
        for tile in collisionslist4:
            if not tile in collisionslist: collisionslist.append(tile)
        
        for i, tile in enumerate(collisionslist):
            disx = tile.centerx - self.player.rect.centerx
            disy = tile.centery - self.player.rect.centery
            dis = abs(disx) + abs(disy)
            if dis > self.player.lookup_radius: collisionslist.pop(i)

        self.player.update(dt, collisionslist)

    def get_chunkpos(self, pos) -> list: return [int(pos[0] // self.camera.tilesize // self.level.chunk_size), int(pos[1] // self.camera.tilesize // self.level.chunk_size)]
    def get_breaking_time(self) -> float: 
        block_on = self.level.world[self.mouse_info[0]][self.mouse_info[1][1]][self.mouse_info[1][0]]
        
        block_selec = self.inventory.get_selec()
        if block_selec[0] in self.level.tools.keys():
            mul = 1 / self.pickaxe["strenght"]
        else: mul = 3

        return (self.level.block_breaking_times[str(self.block_breaking["type"])]) * mul

    def handle_breaking(self) -> None:
        if self.zoom_scroll.rect.collidepoint(self.mspos) or self.zoom_scroll.scrolling or self.inventory.rect.collidepoint(self.mspos): return
        if not self.mouse_info[0] in self.level.world.keys(): return
        if self.inventory.is_clicking: return

        disx = self.player.rect.centerx - self.mscoord[0]
        disy = self.player.rect.centery - self.mscoord[1]
        dis = math.sqrt(disx ** 2 + disy ** 2)
        if dis > self.player.reach: return

        left_click, _, right_click = pygame.mouse.get_pressed()
        block_on = self.level.world[self.mouse_info[0]][self.mouse_info[1][1]][self.mouse_info[1][0]]

        if block_on == 4: return

        # Break blocks
        if left_click:
            if block_on == 0: return
            time_to_break = self.get_breaking_time()
            if self.breaking_block:
                if self.mouse_info[3] == self.block_breaking["abs"]:
                    if (self.block_breaking["begin"] + time_to_break) <= self.actual_time:
                        self.level.destroyat(self.mouse_info[2], self.mouse_info[1])
                        self.breaking_block = False
                        if self.inventory.slots[self.inventory.selected].item_type == "tool":
                            self.inventory.give(block_on)
                        return
                
                else: 
                    self.block_breaking = {
                        "abs": self.mouse_info[3],
                        "begin": self.actual_time,
                        "type": block_on
                    }
            else:
                self.breaking_block = True
                self.block_breaking = {
                    "abs": self.mouse_info[3],
                    "begin": self.actual_time,
                    "type": block_on
                }
        elif right_click:
            if block_on != 0: return

            if self.inventory.slots[self.inventory.selected].item_type == "block":
                if self.inventory.get_nb():
                    self.level.placeat(self.mouse_info[2], self.mouse_info[1], self.level.blocks[self.inventory.slots[self.inventory.selected].item])
                    self.inventory.use()
        
    def update(self, dt) -> None:
        self.mouse_info = self.get_world_pos(self.mscoord)

        self.handle_player_collide(dt)

        pressed = pygame.key.get_pressed()
        if pressed[self.player.keys["left"]]: self.player.LEFT_KEY, self.player.FACING_LEFT = True, True
        else: self.player.LEFT_KEY = False
        if pressed[self.player.keys["right"]]: self.player.RIGHT_KEY, self.player.FACING_LEFT = True, False
        else: self.player.RIGHT_KEY = False
        if pressed[self.player.keys["jump"]]: self.player.jump()
        else: self.player.is_jumping = False

        self.handle_breaking()

        self.adjust_cam()
        self.inventory.update(self.mspos, pressed)
        
    def adjust_cam(self) -> None:
        self.zoom_scroll.update(self.mspos)
        new_tilesize = int(self.zoom_scroll.get_val())
        old_tilesize = self.camera.tilesize
        if new_tilesize != self.camera.tilesize:
            cam_coord = [self.camera.offset.x, self.camera.offset.y]
            player_coord = [self.player.position.x, self.player.position.y]
            player_vel = [self.player.velocity.x, self.player.velocity.y]
            player_acc = [self.player.acceleration.x, self.player.acceleration.y]
            self.camera.tilesize = new_tilesize
            self.camera.offset = pygame.Vector2(cam_coord[0] / old_tilesize * new_tilesize, cam_coord[1] / old_tilesize * new_tilesize)
            self.camera.speed = new_tilesize / self.camera.speed_ratio
            
            self.player.velocity.x, self.player.velocity.y = player_vel[0] / old_tilesize * new_tilesize, player_vel[1] / old_tilesize * new_tilesize
            self.player.acceleration.x, self.player.acceleration.y = player_acc[0] / old_tilesize * new_tilesize, player_acc[1] / old_tilesize * new_tilesize
            self.player.rect.width = new_tilesize / self.player.size_ratio[0]
            self.player.rect.height = new_tilesize / self.player.size_ratio[1]
            self.player.speed = new_tilesize / self.player.speed_ratio
            self.player.max_fall_speed = new_tilesize / self.player.max_fall_speed_ratio
            self.player.jump_height = new_tilesize / self.player.jump_ratio
            self.player.gravity = new_tilesize / self.player.grav_ratio
            self.player.lookup_radius = new_tilesize / self.player.lookup_ratio
            self.player.reach = new_tilesize / self.player.reach_ration
            self.player.acceleration = pygame.Vector2(0, self.player.gravity)
            self.player.position = pygame.Vector2(player_coord[0] / old_tilesize * new_tilesize, player_coord[1] / old_tilesize * new_tilesize)
            self.player.rect.bottomleft = self.player.position

    def run(self) -> None:
        while self.running:
            self.mspos = pygame.mouse.get_pos()
            self.mscoord = self.camera.cam_to_pos(self.mspos)
            self.actual_time = time.perf_counter()
            self.dt = self.clock.tick(self.fps) * 0.001 * self.target_fps
            for event in pygame.event.get():
                if event.type == QUIT: self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE: self.running = False
                    elif event.key == pygame.K_a: self.inventory.use()

            self.update(self.dt)
            
            self.camera.move(inputs=False, dt=self.dt, target=self.player.rect.center)
            self.screen.fill((0, 0, 0))
            self.refresh_screen()
            self.widgets(fps=self.clock.get_fps())
            pygame.display.update()

        try: playerpos = [self.camera.tilesize / self.player.position.x, self.camera.tilesize / self.player.position.y]
        except: playerpos = [0, 0]
        self.level.save(playerpos, self.zoom_scroll.get_val())
        self.inventory.save()
        pygame.quit()
        sys.exit()


game = Main()
game.run()






