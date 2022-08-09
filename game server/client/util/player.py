

class Player:
    def __init__(self, id, position, online) -> None:
        self.id = id
        self.position = position

        self.online = online

        self.rotation = 0

        self.next_pos = position
        self.last_pos = position
        self.next_rot = 0




