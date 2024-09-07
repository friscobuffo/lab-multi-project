import socket
import pickle

class Transmitter:
    def __init__(self) -> None:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('localhost', 12345))

    def send(self, object) -> None:
        message = pickle.dumps(object)
        self.s.sendall(message)
    
    def close(self) -> None:
        self.s.close()