import pygame, sys, time
from _thread import start_new_thread

from util.network import Network
from util.rotation import rot_ratio

from util.player import Player
from camera import Camera


vps1 = ("185.171.202.188", 5555)
vps2 = ("144.24.198.59", 5556)
local = ("0.0.0.0", 6666)

ADDRESS = local



class Game:
    def __init__(self) -> None:
        self.debug = False
        self.received = {}

        self.running = True
        self.fps = 60

        # Combien de fois le client envoie ses infos au serveur (par seconde)
        # ATTENTION -> toujours inférieur au FPS
        self.tps = 5

        self.cooldown_tick = 1 / self.tps
        self.last_tick = -self.cooldown_tick
        self.clock = pygame.time.Clock()

        self.mspos = (0, 0)

        self.players = {}
        for i in range(10): self.players.update({str(i): Player(i, [0, 0], False)})
        
        self.screenw = 500
        self.screenh = 500
        
        self.screen = pygame.display.set_mode((self.screenw, self.screenh), pygame.RESIZABLE)
        pygame.display.set_caption("Client")

        self.keys = {
            "left": pygame.K_q,
            "right": pygame.K_d,
            "up": pygame.K_z,
            "down": pygame.K_s
        }
        self.actual_pressed = {}

        self.map = []

        self.camera = Camera(self.screenw, self.screenh)

    def connect(self, addr):
        self.address, self.port = addr
        
        self.network = Network(self.address, self.port)
        response = self.network.bind()

        if response is None:
            print("An error occured while connecting ...")
            return False
        
        for key in response.keys():
            data = response[key]
            if key == "connected" and data == False:
                print("An error occured while connecting ...")
                return False
            elif key == "id": self.playerID = data
            elif key == "map": self.map = data
            elif key == "tps": self.interpolation_ratio = int(self.fps / data)
        
        start_new_thread(self.auto_receive, ())
        return True
    
    def refresh(self):
        self.screen.fill((0, 0, 0))

        self.camera.render(self.map)
        
        for playerID in self.players.keys():
            player = self.players[playerID]
            if player.online:
                
                dis = 30
                rotated_pos_ratio = rot_ratio(player.rotation)
                rotated_pos = [rotated_pos_ratio[0] * dis + player.position[0], rotated_pos_ratio[1] * dis + player.position[1]]
                
                pygame.draw.circle(self.screen, (255, 255, 255), self.camera.pos_to_cam(player.position), 16)

                pygame.draw.circle(self.screen, (255, 0, 255), self.camera.pos_to_cam(rotated_pos), 5)

        
        x1, y1 = self.camera.pos_to_cam((0, 0))
        x2, y2 = self.camera.pos_to_cam(((len(self.map[0]) * self.camera.tilesize), (len(self.map) * self.camera.tilesize)))
        pygame.draw.line(self.screen, (255, 0, 0), (x1, y1), (x2, y1))
        pygame.draw.line(self.screen, (255, 0, 0), (x2, y1), (x2, y2))
        pygame.draw.line(self.screen, (255, 0, 0), (x2, y2), (x1, y2))
        pygame.draw.line(self.screen, (255, 0, 0), (x1, y2), (x1, y1))
        
        
        pygame.display.update()
    
    def input(self):
        self.actual_pressed = {}
        for index in self.keys.keys():
            if self.pressed[self.keys[index]]:
                self.actual_pressed.update({index: True})
    
    def update(self):
        self.camera.move(self.dt)

        for playerID in self.players:
            player = self.players[playerID]

            if player.online:                
                disx = player.next_pos[0] - player.position[0]
                disy = player.next_pos[1] - player.position[1]
                addx = disx / self.interpolation_ratio
                addy = disy / self.interpolation_ratio
                next_posx = player.position[0] + addx
                next_posy = player.position[1] + addy
                last_posx = (player.position[0] + next_posx) / 2
                last_posy = (player.position[1] + next_posy) / 2
                player.position[0] = last_posx
                player.position[1] = last_posy

                if int(playerID) == self.playerID: self.camera.target = player.position

                disrot = player.next_rot - player.rotation
                if disrot < -180: disrot += 360
                elif disrot > 180: disrot -= 360
                addrot = disrot / self.interpolation_ratio
                player.rotation = (player.rotation + addrot) % 360

        self.input()
        
        if self.actual_time >= (self.last_tick + self.cooldown_tick):
            self.last_tick = self.actual_time
            self.tick()
        
    def tick(self):
        if self.last_mouse_pos[0] != self.mspos[0] or self.last_mouse_pos[1] != self.mspos[1]:
            self.network.add({"mspos": self.mspos})

        if len(self.actual_pressed) != 0: 
            self.network.add({"input": self.actual_pressed})

        if self.debug: 
            print(f"\nSent : {self.network.data}")
            print(f"Received : {self.received}\n")
        self.network.update()

    def auto_receive(self):
        while self.running:
            try:
                self.received = self.network.receive_strong()
                if self.received is None: return
                for key in self.received.keys():
                    data = self.received[key]
                    if key == "disconnect": self.running = False
                    elif key == "players":
                        for key in data.keys():
                            self.players[key].next_pos = data[key]["position"]
                            self.players[key].next_rot = data[key]["rotation"]
                            self.players[key].online = data[key]["online"]
                    elif key == "changeblock": self.map[data[1]][data[0]] = data[2]
                    elif key == "map": self.map = data
                    
                    else: print(f"Unknown data type received : {key} -> {data}")
            except:
                print(f"[ERROR] An error occured while receiving the packets from {self.network.address}")

    def run(self):
        self.running = True
        while self.running:
            self.msscreen = pygame.mouse.get_pos()
            self.last_mouse_pos = [self.mspos[0], self.mspos[1]]
            self.mspos = self.camera.cam_to_pos(self.msscreen)
            self.pressed = pygame.key.get_pressed()

            self.actual_time = time.perf_counter()

            self.dt = self.clock.tick(self.fps) * 0.001 * self.fps

            self.refresh()
            self.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.running = False
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.camera.screenw, self.camera.screenh = event.w, event.h
        
        self.network.quit()




game = Game()
connected = game.connect(ADDRESS)
if connected: game.run()








