import socket
import pickle

import socket
import pickle

class Transmitter:
    def __init__(self, host: str = 'localhost', port: int = 12345, timeout: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soket.settimeout(self.timeout)
        try:
            self.soket.connect((self.host, self.port))
            print("transmitter connected")
        except socket.error as e:
            raise ConnectionError(f"Failed to connect to {self.host}:{self.port}") from e

    def send(self, obj: any) -> None:
        try:
            message = pickle.dumps(obj)
            self.soket.sendall(message)
            print("sent data")
        except (socket.error, pickle.PicklingError) as e:
            raise ConnectionError("Failed to send data") from e

    def close(self) -> None:
        if self.soket:
            self.soket.close()