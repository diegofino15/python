import socket, pickle


class Network:
    def __init__(self, address, port) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = address
        self.port = port

        self.address = (self.server, self.port)

    def bind(self):
        self.data = {}

        return self.connect()
    
    def connect(self):
        try:
            self.client.connect(self.address)
            received = self.receive_strong()

            return received
        
        except: return None
    
    def receive_strong(self):
        received = self.client.recv(4096)
        size = int.from_bytes(received[0:3], 'little')
        r_data = []
        r_data.append(received[4:])
        while len(b"".join(r_data)) < size:
            packet = self.client.recv(4096)
            if not packet: break
            r_data.append(packet)

        all_data = b"".join(r_data)
        data_arr = pickle.loads(all_data) if all_data != b"" else None
        return data_arr
    
    def send_strong(self, what):
        pickled_data = pickle.dumps(what)
        length = len(pickled_data).to_bytes(4, 'little')
        self.client.send(length)
        self.client.send(pickled_data)
    
    def quit(self): self.send_strong({"quit": None})

    def add(self, data): self.data.update(data)

    def update(self): 
        if len(self.data) == 0: self.data.update({"handle": None})
        self.send_strong(self.data)
        self.data = {}


