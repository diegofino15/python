import pygame, json
from util.blocks import items, itemset, get_texture
from sprites.block import Item



class Slot:
    def __init__(self, index, item, nb_item) -> None:
        self.index = index

        self.item = item
        self.nb_items = nb_item

    def empty(self) -> bool:
        if self.nb_items > 0: return False
        return True
    def full(self) -> bool:
        if self.nb_items >= 64: return True
        return False

    def set(self, item, nb=1) -> None:
        self.item = item
        self.nb_items = nb

        if self.nb_items == 0: self.reset()

    def add(self, amount=1) -> int: 
        self.nb_items += amount
        if self.nb_items > 64:
            overload = self.nb_items - 64
            self.nb_items = 64
            return overload
        return 0
    def remove(self, amount=1) -> None: 
        if self.nb_items >= amount: 
            self.nb_items -= amount
        if self.nb_items <= 0: self.reset()

    def reset(self) -> None:
        self.item = None
        self.nb_items = 0

    def copy(self): return Slot(self.index, self.item, self.nb_items)



class Inventory:
    def __init__(self, pos, slots, slotsize, spacement, game) -> None:
        width = (slotsize + spacement) * slots + spacement
        height = slotsize + spacement * 2
        self.rect = pygame.Rect(pos.x, pos.y, width, height)

        self.surface = pygame.Surface((width, height))
        self.surface.set_alpha(100)
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

        self.is_clicking = False
        self.is_dragging = False
        self.slot_clicked = 0

        self.font = pygame.font.Font(None, 20)

        self.screen = pygame.display.get_surface()

        self.game = game

    def get_type(self) -> str: return items[str(self.slots[self.selected].item)]["type"]
    def get_selected(self) -> Slot: return self.slots[self.selected]
    def get_selected_amount(self) -> int: return self.slots[self.selected].nb_items

    def give(self, item_id, nb=1) -> int: # Return the overload
        item_id = str(item_id)
        if items[str(item_id)]["stackable"]:
            for slot in self.slots:    
                if str(slot.item) == str(item_id) and not slot.full():
                    remaining = slot.add(nb)
                    if remaining == 0: return 0
                    for newslot in self.slots:
                        if (str(newslot.item) == str(item_id) or newslot.empty()) and newslot.index != slot.index:
                            if newslot.empty():
                                newslot.set(item_id, 1)
                                remaining = newslot.add(remaining - 1)
                            else: remaining = newslot.add(remaining)
                            if remaining == 0: return 0


        remaining = nb
        for slot in self.slots:
            if slot.empty():
                slot.set(item_id, 1)
                remaining = slot.add(remaining - 1)
                if (remaining - 1) == 0: return
        
        
        return remaining
    def take(self, nb=1) -> None: self.slots[self.selected].remove(nb)
    def clear(self) -> None: self.slots = [Slot(i, None, 0) for i in range(self.nb_slots)]

    def swap(self, slotid1, slotid2) -> None:
        slot1 = self.slots[slotid1].copy()
        slot2 = self.slots[slotid2].copy()

        self.slots[slotid1] = slot2
        self.slots[slotid2] = slot1

        for i, slot in enumerate(self.slots): slot.index = i

        self.selected = slotid2
    
    def update(self, pressed, mspos) -> None:
        if pressed[pygame.K_1]: self.selected = 0
        elif pressed[pygame.K_2]: self.selected = 1
        elif pressed[pygame.K_3]: self.selected = 2
        elif pressed[pygame.K_4]: self.selected = 3
        elif pressed[pygame.K_5]: self.selected = 4
        elif pressed[pygame.K_6]: self.selected = 5
        elif pressed[pygame.K_7]: self.selected = 6
        elif pressed[pygame.K_8]: self.selected = 7
        elif pressed[pygame.K_9]: self.selected = 8
        elif pressed[pygame.K_0]: self.selected = 9

        for slot in self.slots:
            if slot.empty(): slot.reset()

        if pygame.mouse.get_pressed()[0]:
            if not self.is_clicking:
                if self.rect.collidepoint(mspos):
                    for i, slot in enumerate(self.slots):
                        rect = self.rects[i]
                        if rect.collidepoint(mspos):
                            self.slot_clicked = i
                            break
                    self.is_clicking = True
                
                else: self.is_clicking = False
            else:
                if self.rects[self.slot_clicked].collidepoint(mspos):
                    self.is_dragging = False
                else: self.is_dragging = True
        else:
            if self.is_clicking:
                self.is_clicking = False
                for i, slot in enumerate(self.slots):
                    if self.slots[self.slot_clicked].empty(): break
                    rect = self.rects[i]
                    if rect.collidepoint(mspos):
                        if i != self.slot_clicked:
                            if slot.item == self.slots[self.slot_clicked].item and items[str(slot.item)]["stackable"]:
                                over = slot.add(self.slots[self.slot_clicked].nb_items)
                                self.slots[self.slot_clicked].reset()
                                self.slots[self.slot_clicked].set(slot.item, over)

                                self.selected = i
                            else:
                                if self.is_dragging:
                                    self.swap(self.slot_clicked, i)
                                self.is_dragging = False
                        break

                if not self.is_dragging:
                    for i, slot in enumerate(self.slots):
                        rect = self.rects[i]
                        if rect.collidepoint(mspos):
                            self.selected = i
                            return

    def drop(self, amount=1) -> None:
        if self.slots[self.selected].item is not None: 
            itemid = self.slots[self.selected].item
            self.game.items_on_ground.append(Item(self.game.mscoord, itemid, 16, self.game.world, self.game.player, self.game.actual_time, amount))
            self.take(amount)

    def draw(self, mspos) -> None:
        offset = 8
        
        pygame.draw.rect(self.screen, (80, 80, 80), self.rect, border_radius=3)
        pygame.draw.rect(self.screen, (50, 50, 50), self.rect, border_radius=3, width=3)

        self.surface.fill((20, 20, 20))
        self.icon_surface.fill((20, 20, 20))

        size = int(self.slotsize - offset * 2)
        
        for i, slot in enumerate(self.slots):
            rect = self.rects[i]
            if slot.index == self.selected: 
                color = (0, 0, 0)
                width = 5
            else: 
                color = (40, 40, 40)
                width = 3

            pygame.draw.rect(self.surface, color, (rect.left - self.rect.left, rect.top - self.rect.top, rect.width, rect.height), border_radius=3, width=width)
            if self.is_dragging and self.is_clicking and i == self.slot_clicked: continue

            if not slot.empty():
                image = get_texture(items[str(slot.item)]["texture"], file=itemset)
                x, y = int(rect.left + offset), int(rect.top + offset)
                image = pygame.transform.scale(image, (size, size))
                new_rect = image.get_rect(topleft=(x, y))
                self.icon_surface.blit(image, (x - self.rect.left, y - self.rect.top))
                
                if items[str(slot.item)]["stackable"]:
                    textsurf = self.font.render(str(slot.nb_items), True, "white")
                    self.icon_surface.blit(textsurf, (new_rect.right - self.rect.left, new_rect.bottom - self.rect.top))
        
        if self.is_dragging and self.is_clicking:
            slot = self.slots[self.slot_clicked]
            if not slot.empty(): 
                if not self.rects[self.slot_clicked].collidepoint(mspos):
                    x, y = int(mspos[0] - rect.width // 2), int(mspos[1] - rect.height // 2)
                else:
                    x, y = self.rects[self.slot_clicked].topleft
                
                image = get_texture(items[str(slot.item)]["texture"], file=itemset)
                image = pygame.transform.scale(image, (size, size))
                new_rect = image.get_rect(topleft=(x, y))

                self.screen.blit(image, (x, y))

                if items[str(slot.item)]["stackable"]:
                    textsurf = self.font.render(str(slot.nb_items), True, "white")
                    self.screen.blit(textsurf, (new_rect.right, new_rect.bottom))
        
        self.screen.blit(self.surface, self.rect.topleft)
        self.screen.blit(self.icon_surface, self.rect.topleft)
        
        if not self.slots[self.selected].empty():
            text = items[str(self.slots[self.selected].item)]["name"]
            textsurf = self.font.render(text, True, "white")
            self.screen.blit(textsurf, (self.rect.left, self.rect.bottom))

    def save(self) -> None:
        data = []
        for i, slot in enumerate(self.slots):
            data.append([i, slot.item, slot.nb_items])

        with open("./worlds/inventory.json", "w") as file:
            json.dump(data, file)
            file.close()
    
    def load(self) -> list:
        try:
            with open("./worlds/inventory.json", "r") as file:
                data = json.load(file)
                file.close()
            
            slots = []
            for i, slot in enumerate(data):
                slots.append(Slot(i, slot[1], slot[2]))

            return slots
       
        except:
            return [Slot(i, None, 0) for i in range(self.nb_slots)]


    


