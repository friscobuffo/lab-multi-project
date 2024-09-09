import socket
import pickle

class Receiver:
    def __init__(self, host: str = 'localhost', port: int = 12345, timeout: float = 120.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soket.settimeout(self.timeout)
        self.soket.bind((self.host, self.port))
        self.soket.listen(1)
        try:
            self.connection, self.address = self.soket.accept()
        except socket.timeout as e:
            raise TimeoutError("Connection timed out while waiting for a client") from e
        return self

    def receive(self) -> any:
        try:
            data = b""
            while True:
                packet = self.connection.recv(4096)
                if not packet:  # No more data, stop receiving
                    break
                data += packet
            print("received data")
            return pickle.loads(data)  # Deserialize the received data
        except (socket.error, pickle.UnpicklingError) as e:
            raise ConnectionError("Failed to receive or decode data") from e

    def close(self) -> None:
        if self.connection:
            self.connection.close()
        if self.soket:
            self.soket.close()

# Example usage:
# with Receiver() as receiver:
#     data = receiver.receive()
#     print("Received:", data)