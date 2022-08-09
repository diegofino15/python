import socket, math
from _thread import start_new_thread
from pygame.time import Clock

from player import Player
from sender import Sender
from level import LEVEL
from util.util import say


vps1 = ("185.171.202.188", 5555)
vps2 = ("144.24.198.59", 5556)
local = ("0.0.0.0", 6666)

ADDRESS = local


class Client:
    def __init__(self, connection, playerID, players, map, tps) -> None:
        self.connection = connection
        self.playerID = playerID

        self.last_players_data = {}

        self.players = players
        self.player = self.players[str(self.playerID)]

        self.sender = Sender(self.connection)

        self.connected = True

        self.map, self.tps = map, tps
    
    def auto_send(self):
        clock = Clock()
        while self.player.online:
            data = {}
            for key in self.players:
                otherp = self.players[key]
                player_data = {
                    "position": [int(otherp.position[0]), int(otherp.position[1])],
                    "rotation": otherp.rotation,
                    "online": otherp.online
                }

                data.update({str(otherp.id): player_data})

            real_data = {}

            for playerID in data.keys():
                if playerID in self.last_players_data.keys():
                    if self.last_players_data[playerID]["position"][0] != data[playerID]["position"][0] or self.last_players_data[playerID]["position"][1] != data[playerID]["position"][1]:
                        real_data.update({playerID: data[playerID]})
                    elif self.last_players_data[playerID]["rotation"] != data[playerID]["rotation"]:
                        real_data.update({playerID: data[playerID]})
                else: real_data.update({playerID: data[playerID]})

            
            self.last_players_data = data.copy()
            self.sender.add({"players": real_data})
            self.sender.send()

            clock.tick(self.tps)
    
    def auto_receive(self):
        while self.connected:
            try:
                received = self.sender.receive_strong()
                if not received:
                    say(f"[DISCONNECTED] Player {self.playerID} disconnected")
                    self.connected = False
                else:
                    self.player.moving_left = False
                    self.player.moving_right = False
                    self.player.moving_up = False
                    self.player.moving_down = False

                    for key in received.keys():
                        given_data = received[key]

                        if key == "handle": pass
                        elif key == "message": say(f"[MESSAGE] <player {self.playerID}> {given_data}")
                        elif key == "quit":
                            say(f"[DISCONNECTED] Player {self.playerID} disconnected")
                            self.connected = False
                        elif key == "mspos":
                            lastpos = self.player.position
                            nextpos = [self.player.position[0] + self.player.velocity.x, self.player.position[1] + self.player.velocity.y]
                            A = [(lastpos[0] + nextpos[0]) / 2, (lastpos[1] + nextpos[1]) / 2]
                            C = given_data

                            AB = C[0] - A[0]
                            BC = C[1] - A[1]
                            if AB == 0 or BC == 0: continue
                            
                            AC = math.sqrt(AB ** 2 + BC ** 2)
                            rot = math.acos(AB / AC) / math.pi * 180
                            if C[1] < A[1]: rot += (180 - rot) * 2

                            self.player.rotation = int(rot)
                        
                        elif key == "input":
                            for pressed in given_data:
                                if pressed == "left": self.player.moving_left = True
                                elif pressed == "right": self.player.moving_right = True
                                elif pressed == "up": self.player.moving_up = True
                                elif pressed == "down":self. player.moving_down = True
                
            except: break
        
        self.player.online = False
        say(f"[DISCONNECTED] Player {self.playerID} lost connection")
        self.connection.close()

    def start(self):
        self.sender.send_strong({"connected": True, "id": self.playerID, "map": self.map, "tps": self.tps})

        start_new_thread(self.auto_send, ())
        start_new_thread(self.auto_receive, ())


class Server:
    def __init__(self) -> None:
        self.address = ADDRESS[0]
        self.port = ADDRESS[1]
        self.started = False

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.map = LEVEL

        self.tilesize = 64

        # Combien de fois le serveur envoie les infos au joueur (par seconde)
        self.tps = 20

        self.players_connected = {}
        for i in range(10): self.players_connected.update({str(i): Player(i, [0, 0], False, 32, self.map, self.tilesize, -.12)})

        start_new_thread(self.update_players, ())

    def update_players(self):
        clock = Clock()
        while True:
            dt = clock.tick(60) * 0.001 * 60
            for key in self.players_connected:
                player = self.players_connected[key]
                if player.online:
                    player.update(dt)
    
    def start_new_client(self, connection, playerID):
        client = Client(connection, playerID, self.players_connected, self.map, self.tps)
        self.players_connected[str(playerID)].online = True
        client.start()

    def run(self):
        try: self.s.bind((self.address, self.port))
        except socket.error as e: 
            print(str(e))
            return
        except:
            say(f"An unknown error occured")
            return

        self.s.listen(2)

        say(f"[SERVER] Server started on port {self.port}")
        say("[SERVER] Waiting for connection ...")

        self.current_player = 0

        self.started = True
        while True:
            try:
                connection, address = self.s.accept()
                say(f"[CONNECTED] {address[0]} connected at port {address[1]} -> player {self.current_player}")

                self.start_new_client(connection, self.current_player)
                self.current_player += 1
            except KeyboardInterrupt:
                say("[SERVER] Closing ...", new_line=True)
                break

        say("[SERVER] Server closed")




server = Server()
server.run()



