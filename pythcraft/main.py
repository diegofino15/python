import pygame, time
from pygame import Vector2
from _thread import start_new_thread as new_thread

from sprites.block import Block, Item
from sprites.player import Player

from camera import Camera
from util.world import World
from util.blocks import blocks, items

from gui.debug import debug
from gui.chat import Chat


class Game:
    def __init__(self) -> None:
        self.fps = 60
        self.tps = 30
        self.cooldown_tick = 1 / self.tps
        self.last_tick = 0

        screenw, screenh = 1280, 720

        self.world = World()

        self.camera = Camera(screenw, screenh, self.fps, self.world)

        width, height = 500, 300
        self.chat = Chat(Vector2(screenw - width, 0), width, height, 5, "black", "white")
        self.world.set_chat(self.chat)

        infos = self.world.load()
        if infos:
            playerpos = infos["playerpos"]
            playervel = infos["playervel"]
            tilesize = infos["tilesize"]

            playerpos = Vector2(playerpos.x / tilesize * self.world.tilesize, playerpos.y / tilesize * self.world.tilesize)
            playervel = Vector2(playervel.x / tilesize * self.world.tilesize, playervel.y / tilesize * self.world.tilesize)
        else:
            playerpos = Vector2(0, 0)
            playervel = Vector2(0, 0)

        speed = 0.5 / 16 * self.world.tilesize
        jumpheight = 9 / 16 * self.world.tilesize
        sizex = int(14 / 16 * self.world.tilesize)
        sizey = int(29 / 16 * self.world.tilesize)
        self.player = Player(self.world.gravity, self.world.friction, speed, jumpheight, (sizex, sizey), self.world, self, pos=playerpos, vel=playervel)
        self.world.add_entity(self.player)
        self.world.set_player(self.player)
        self.camera.position = self.camera.coord_to_pos(self.player.position)

        self.dt = 1
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.get_surface()

        self.running = True

        self.mouse_on_gui = False
        self.gui_rects = []
        self.gui_rects.append(self.player.inventory.rect)

        self.items_on_ground = []

        new_thread(self.generate_world, ())
        new_thread(self.auto_physics, ())
    
    def generate_world(self) -> None:
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(5)

            minimum = self.camera.pos_to_coord(self.camera.cam_to_pos(Vector2(self.camera.rect.left - self.camera.screenw // 2, self.camera.rect.top - self.camera.screenh // 2)))
            maximum = self.camera.pos_to_coord(self.camera.cam_to_pos(Vector2(self.camera.rect.right + self.camera.screenw // 2, self.camera.rect.bottom + self.camera.screenh // 2)))

            minx = minimum.x // self.world.chunksize // self.world.tilesize
            maxx = maximum.x // self.world.chunksize // self.world.tilesize

            miny = minimum.y // self.world.chunksize // self.world.tilesize
            maxy = maximum.y // self.world.chunksize // self.world.tilesize

            for i in range(int(minx), int(maxx) + 1):
                for j in range(int(miny), int(maxy) + 1):
                    addr = (i, j)
                    self.world.generate_chunk(addr)
    
    def auto_physics(self) -> None:
        clock = pygame.time.Clock()
        while self.running:
            dt = clock.tick(self.tps) * 0.001 * self.tps
            for i, item in enumerate(self.items_on_ground):
                item.update(dt, self.actual_time)
                if not item.existing: self.items_on_ground.pop(i)

    def update(self) -> None:
        for entity in self.world.entities:
            entity.update(self.dt)
        
        self.player.input(self.pressed)
        self.player.inventory.update(self.pressed, self.msscreen)
        self.camera.move(self.player, self.dt)

        self.chat.update(self.actual_time)
        
        self.mouse_on_gui = False
        for rect in self.gui_rects:
            if rect.collidepoint(self.msscreen):
                self.mouse_on_gui = True
                break
        if self.player.inventory.is_clicking and self.player.inventory.is_dragging: self.mouse_on_gui = True

        self.handle_player_actions()
    
    def handle_player_actions(self) -> None:
        if not self.mouse_on_gui:
            if pygame.mouse.get_pressed()[0]:
                block = self.getblockat(self.mscoord)
                selected = self.player.inventory.get_selected()
                if block is None or block.unbreakable: return
                if not self.player.breaking_block:
                    self.player.breaking_block = True
                    self.player.time_to_break_block = self.calculate_time(block)
                    self.player.time_begin_breaking = self.actual_time
                    self.player.block_breaking = block
                else:
                    if self.player.block_breaking is block and self.player.slot_breaking == self.player.inventory.selected:
                        if (self.player.time_begin_breaking + self.player.time_to_break_block) <= self.actual_time:
                            self.player.breaking_block = False
                            if self.placeblock(self.mscoord, None):
                                can_receive_block = False
                                
                                if selected.item is None or items[str(selected.item)]["type"] == "block":
                                    if "hand" in blocks[str(block.id)]["tools-to-break"]: can_receive_block = True
                                elif items[str(selected.item)]["tooltype"] in blocks[str(block.id)]["tools-to-break"]: can_receive_block = True
                                
                                if can_receive_block:
                                    for item, nb in blocks[str(block.id)]["drops"]:
                                        self.items_on_ground.append(Item(self.mscoord, item, 16, self.world, self.player, self.actual_time, nb))
                    else:
                        self.player.time_to_break_block = self.calculate_time(block)
                        self.player.time_begin_breaking = self.actual_time
                        self.player.block_breaking = block
                        self.player.slot_breaking = self.player.inventory.selected
            
            else: self.player.breaking_block = False

            if pygame.mouse.get_pressed()[2]: 
                selected = self.player.inventory.get_selected()
                if selected.item is None or items[str(selected.item)]["type"] != "block": return
                elif self.getblockat(self.mscoord) is not None: return
                blockid = items[str(selected.item)]["blockid"]
                
                if self.placeblock(self.mscoord, Block(self.mscoord, blockid, self.world.tilesize)):
                    self.player.inventory.take()

    def calculate_time(self, block) -> float:
        selected = self.player.inventory.get_selected()
        if selected.item is None or items[str(selected.item)]["type"] == "block": return blocks[str(block.id)]["resistance"] * 2
        
        selected_id = str(selected.item)
        if items[selected_id]["type"] == "tool" and items[selected_id]["tooltype"] == blocks[str(block.id)]["tool"]: diviser = 2 * items[selected_id]["strenght"]
        else: diviser = 0.5
        
        return blocks[str(block.id)]["resistance"] / 2 / diviser

    def gui(self) -> None:
        self.chat.draw()
        self.player.inventory.draw(self.msscreen)

        debug([f"FPS -> {int(self.clock.get_fps())}", f"BLOCKSIZE -> {self.camera.blocksize}"], side="right", y="top", color="black")

    def refresh(self) -> None:
        # RESET THE DISPLAY
        self.screen.fill((80, 100, 150))
        
        # RENDER THE BLOCKS AND THE ENTITIES
        self.camera.render(self.world)
        for entity in self.world.entities:
            self.camera.draw(entity.image, entity.rect)
        for item in self.items_on_ground:
            pos = self.camera.coord_to_cam(Vector2(item.drawrect.left, item.drawrect.top))
            self.screen.blit(item.image, (int(pos.x), int(pos.y)))
        
        # DRAW MOUSE POSITION
        #mschunkx = self.mscoord.x // self.world.chunksize // self.world.tilesize
        #mschunky = self.mscoord.y // self.world.chunksize // self.world.tilesize
        #screenmschunk = self.camera.pos_to_cam(Vector2(mschunkx * self.world.chunksize * self.camera.blocksize, mschunky * self.world.chunksize * self.camera.blocksize))
        #pygame.draw.rect(self.screen, "black", (screenmschunk.x, screenmschunk.y, self.world.chunksize * self.camera.blocksize, self.world.chunksize * self.camera.blocksize), width=3)
        pos = self.camera.pos_to_cam(Vector2(self.mspos.x // self.camera.blocksize * self.camera.blocksize, self.mspos.y // self.camera.blocksize * self.camera.blocksize))
        pygame.draw.rect(self.screen, "black", (pos.x, pos.y, self.camera.blocksize, self.camera.blocksize), width=2)

        # DRAW THE GUI
        self.gui()

        # UPDATE THE SCREEN
        pygame.display.update()

    def tick(self) -> None:
        if self.pressed[pygame.K_a]: self.player.inventory.drop()

    def run(self) -> None:
        while self.running:
            mspos = pygame.mouse.get_pos()

            self.msscreen = Vector2(mspos[0], mspos[1])
            self.mspos = self.camera.cam_to_pos(self.msscreen)
            self.mscoord = self.camera.pos_to_coord(self.mspos)

            self.dt = self.clock.tick(self.fps) * 0.001 * self.tps

            self.pressed = pygame.key.get_pressed()
            self.actual_time = time.perf_counter()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                    elif event.key == pygame.K_t: self.chat.last_message = self.actual_time

            # UPDATE
            self.update()

            # DRAW
            self.refresh()

            # TICK
            if (self.last_tick + self.cooldown_tick) <= self.actual_time: 
                self.tick()
                self.last_tick = self.actual_time

        pygame.quit()
        
        self.world.save()
        self.player.inventory.save()

    def placeblock(self, coord, block) -> bool:
        rect = pygame.Rect(coord.x // self.world.tilesize * self.world.tilesize, coord.y // self.world.tilesize * self.world.tilesize, self.world.tilesize, self.world.tilesize)
        if not self.player.rect.colliderect(rect): return self.setblock(coord, block)
        return False

    def setblock(self, coord, block) -> bool:
        posx = coord.x // self.world.tilesize
        posy = coord.y // self.world.tilesize

        chunkx = posx // self.world.chunksize
        chunky = posy // self.world.chunksize

        newposx = posx - (chunkx * self.world.chunksize)
        newposy = posy - (chunky * self.world.chunksize)

        addr = (chunkx, chunky)
        if addr in self.world.chunks.keys():
            self.world.chunks[addr][int(newposy)][int(newposx)] = block
            self.camera.modified.append(addr)
            return True
        return False

    def getblockat(self, coord) -> Block:
        posx = coord.x // self.world.tilesize
        posy = coord.y // self.world.tilesize
        chunkx = posx // self.world.chunksize
        chunky = posy // self.world.chunksize
        newposx = posx - (chunkx * self.world.chunksize)
        newposy = posy - (chunky * self.world.chunksize)

        addr = (chunkx, chunky)
        if addr in self.world.chunks.keys():
            return self.world.chunks[addr][int(newposy)][int(newposx)]
        return None


PythCraft = Game()
PythCraft.run()









