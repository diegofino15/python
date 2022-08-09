import pygame, json
from ressources.textures import items, blocks


item_types = {
    "pickaxe": "tool",
    
    "stone": "block",
    "grass": "block",
    "dirt": "block",
    
}



class Slot:
    def __init__(self, index, item, nb_item) -> None:
        self.item = item
        self.item_type = item_types[item] if item is not None else None
        self.nb_items = nb_item

        self.index = index
        
    def empty(self) -> bool:
        if self.nb_items > 0: return False
        return True
    def full(self) -> bool:
        if self.nb_items >= 64: return True
        return False

    def update(self) -> None:
        if self.empty():
            self.reset()
        if self.nb_items > 64: self.nb_items = 64

    def add(self, amount=1) -> int: 
        self.nb_items += amount
        if self.nb_items > 64:
            return self.nb_items - 64
        return 0
    def remove(self, amount=1) -> None: 
        if self.nb_items > 0: 
            self.nb_items -= amount
    def clear(self) -> None: self.nb_items = 0

    def reset(self) -> None:
        self.item = None
        self.nb_items = 0
        self.item_type = None


class Inventory:
    def __init__(self, pos, slots, slotsize, spacement, level) -> None:
        width = (slotsize + spacement) * slots + spacement
        height = slotsize + spacement * 2
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

        self.surface = pygame.Surface((width, height))
        self.surface.set_colorkey((20, 20, 20))

        self.icon_surface = self.surface.copy()
        self.icon_surface.set_colorkey((20, 20, 20))

        self.nb_slots = slots
        self.spacement = spacement
        self.slotsize = slotsize

        self.slots = self.load()
        
        self.rects = []
        for i in range(slots):
            x = spacement + (slotsize + spacement) * i + pos[0]
            rect = pygame.Rect(x, pos[1] + spacement, slotsize, slotsize)
            self.rects.append(rect)
        
        self.selected = 0
        self.level = level

        self.is_clicking = False
        self.is_dragging = False
        self.slot_clicked = 0

        self.font = pygame.font.Font(None, 20)
        
    def draw(self, surf) -> None:
        pygame.draw.rect(surf, (100, 100, 100), self.rect, border_radius=3)
        pygame.draw.rect(surf, (50, 50, 50), self.rect, border_radius=3, width=3)
        mspos = pygame.mouse.get_pos()
        self.surface.fill((20, 20, 20))
        self.icon_surface.fill((20, 20, 20))

        for slot in self.slots: 
            rect = self.rects[slot.index]
            if slot.index == self.selected: color = (50, 50, 50)
            else: color = (80, 80, 80)
            pygame.draw.rect(self.surface, color, (rect.left - self.rect.left, rect.top - self.rect.top, rect.width, rect.height), border_radius=3, width=3)
            if self.is_dragging and self.is_clicking:
                if slot.index == self.slot_clicked: continue
            if not slot.empty():
                if slot.item_type == "block": 
                    for i, name in blocks.keys():
                        if name == slot.item:
                            img = blocks[(i, name)]
                    of = 8
                else: 
                    img = items[slot.item]["img"]
                    of = 0
                
                x, y = rect.left + of, rect.top + of
                
                new_size = (self.slotsize - of * 2, self.slotsize - of * 2)
                img = pygame.transform.scale(img, new_size)
                new_rect = img.get_rect(topleft=(x, y))
                
                self.icon_surface.blit(img, (int(x) - self.rect.left, int(y) - self.rect.top))

                if slot.item_type != "tool":
                    textsurf = self.font.render(str(slot.nb_items), True, "white")
                    self.icon_surface.blit(textsurf, (new_rect.right - self.rect.left, new_rect.bottom - self.rect.top))
        
        if self.is_dragging and self.is_clicking:
            try:
                slot = self.slots[self.slot_clicked]
                if slot.item_type == "block": 
                    for i, name in blocks.keys():
                        if name == slot.item:
                            img = blocks[(i, name)]
                    of = 8
                else:
                    img = items[slot.item]["img"]
                    of = 0
                if not self.rects[self.slot_clicked].collidepoint(mspos):
                    x, y = mspos[0] - rect.width // 2, mspos[1] - rect.height // 2
                else:
                    x, y = self.rects[self.slot_clicked].topleft
                new_size = (self.slotsize - of * 2, self.slotsize - of * 2)
                img = pygame.transform.scale(img, new_size)
                new_rect = img.get_rect(topleft=(x, y))
                self.icon_surface.blit(img, (int(x) - self.rect.left, int(y) - self.rect.top))
                if slot.item_type != "tool":
                    textsurf = self.font.render(str(slot.nb_items), True, "white")
                    self.icon_surface.blit(textsurf, (new_rect.right - self.rect.left, new_rect.bottom - self.rect.top))
            except: print("Error")
        
        surf.blit(self.surface, self.rect.topleft)
        surf.blit(self.icon_surface, self.rect.topleft)
    
    def get_selec(self) -> list: return [self.slots[self.selected].item, self.selected]
    def get_nb(self) -> int: return self.slots[self.selected].nb_items

    def give(self, block) -> None:
        for blockname in self.level.blocks.keys():
            blockid = self.level.blocks[blockname]

            if blockid == block:
                available_slots = [i for i, slot in enumerate(self.slots) if slot.item == blockname]
                for i in available_slots:
                    if not self.slots[i].full():
                        self.slots[i].add()
                        return
                empty_slots = [i for i, slot in enumerate(self.slots) if slot.item is None or slot.nb_items == 0]
                for i in empty_slots:
                    self.slots[i].item = blockname
                    self.slots[i].item_type = item_types[blockname]
                    self.slots[i].add()
                    return
    
    def update(self, mspos, pressed) -> None:
        if pressed[pygame.K_1]: self.selected = 0
        if pressed[pygame.K_2]: self.selected = 1
        if pressed[pygame.K_3]: self.selected = 2
        if pressed[pygame.K_4]: self.selected = 3
        if pressed[pygame.K_5]: self.selected = 4
        if pressed[pygame.K_6]: self.selected = 5
        if pressed[pygame.K_7]: self.selected = 6
        if pressed[pygame.K_8]: self.selected = 7
        if pressed[pygame.K_9]: self.selected = 8
        if pressed[pygame.K_0]: self.selected = 9

        for slot in self.slots: slot.update()
        
        if pygame.mouse.get_pressed()[0]:
            if not self.is_clicking:
                if self.rect.collidepoint(mspos):
                    for i, slot in enumerate(self.slots):
                        rect = self.rects[i]
                        if rect.collidepoint(mspos):
                            self.slot_clicked = i
                            break
                    self.is_clicking = True
                    self.is_dragging = True
                
                else: self.is_clicking = False
            else:
                if self.rects[self.slot_clicked].collidepoint(mspos):
                    self.is_dragging = False
                else: self.is_dragging = True
        else:
            if self.is_clicking:
                for i, slot in enumerate(self.slots):
                    rect = self.rects[i]
                    if rect.collidepoint(mspos):
                        if i != self.slot_clicked:
                            if slot.item == self.slots[self.slot_clicked].item:
                                over = slot.add(self.slots[self.slot_clicked].nb_items)
                                self.slots[self.slot_clicked].clear()
                                self.slots[self.slot_clicked].add(over)

                                self.is_clicking = False
                                self.selected = i
                                return
                            else:

                                self.swap(i, self.slot_clicked)
                                self.is_clicking = False
                                if self.selected == self.slot_clicked:
                                    self.selected = i
                            return
            if not self.is_dragging and self.is_clicking:
                for i, slot in enumerate(self.slots):
                    rect = self.rects[i]
                    if rect.collidepoint(mspos):
                        self.selected = i
                        self.is_clicking = False
                        return

    def swap(self, index1, index2):
        new_slots = []
        
        for i, slot in enumerate(self.slots):
            if i == index1:
                slot.index = index2
                new_slots.append(self.slots[index2])
            elif i == index2:
                slot.index = index1
                new_slots.append(self.slots[index1])
            else:
                slot.index = i
                new_slots.append(slot)
        
        self.slots = new_slots
    
    def use(self) -> None: self.slots[self.selected].remove()
    
    def save(self) -> None:
        data = []
        for i, slot in enumerate(self.slots):
            data.append([i, not slot.empty(), slot.item, slot.nb_items])


        with open("worlds/player.json", "w") as file:
            json.dump(data, file)
            file.close()
    
    def load(self) -> list:
        try:
            with open("worlds/player.json", "r") as file:
                data = json.load(file)
                file.close()
            
            slots = []
            for i, slot in enumerate(data):
                slots.append(Slot(i, slot[2], slot[3]))

            return slots
       
        except:
            slots = []
            for i in range(self.nb_slots):
                slots.append(Slot(i, None, 0))

            slots[0].item = "pickaxe"
            slots[0].item_type = "tool"
            slots[0].nb_items = 1

            return slots


