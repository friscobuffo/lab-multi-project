import socket
import pickle

import socket
import pickle

class Transmitter:
    def __init__(self, host: str = 'localhost', port: int = 12345, timeout: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.soket = None

    def __enter__(self) -> 'Transmitter':
        self.soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soket.settimeout(self.timeout)
        try:
            self.soket.connect((self.host, self.port))
        except socket.error as e:
            raise ConnectionError(f"Failed to connect to {self.host}:{self.port}") from e
        return self

    def send(self, obj: any) -> None:
        try:
            message = pickle.dumps(obj)
            self.soket.sendall(message)
        except (socket.error, pickle.PicklingError) as e:
            raise ConnectionError("Failed to send data") from e

    def close(self) -> None:
        if self.soket:
            self.soket.close()

    def __exit__(self) -> None:
        self.close()

# Example usage:
# with Transmitter() as transmitter:
#     transmitter.send({'key': 'value'})


# class Transmitter:
#     def __init__(self) -> None:
#         self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.s.connect(('localhost', 12345))

#     def send(self, object) -> None:
#         message = pickle.dumps(object)
#         self.s.sendall(message)
    
#     def close(self) -> None:
#         self.s.close()