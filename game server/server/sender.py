import pickle


class Sender:
    def __init__(self, connection) -> None:
        self.data = {}

        self.connection = connection
    
    def add(self, data): self.data.update(data)
        
    def send_strong(self, what):
        pickled_data = pickle.dumps(what)
        length = len(pickled_data).to_bytes(4, 'little')
        self.connection.send(length)
        self.connection.send(pickled_data)

    def receive_strong(self):
        received = self.connection.recv(4096)
        size = int.from_bytes(received[0:3], 'little')
        r_data = []
        r_data.append(received[4:])
        while len(b"".join(r_data)) < size:
            packet = self.connection.recv(4096)
            if not packet: break
            r_data.append(packet)

        all_data = b"".join(r_data)
        data_arr = all_data if all_data != b"" else None
        return pickle.loads(data_arr)
    
    def send(self):
        self.send_strong(self.data)
        self.data = {}



