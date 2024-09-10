import socket
import pickle
import struct

class Transmitter:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 9999))
    
    def send(self, obj: any) -> None:
        print("Sending data...")
        try:
            serialized = pickle.dumps(obj)
            message = struct.pack("Q", len(serialized)) + serialized
            self.client_socket.sendall(message)
            print("Data sent")
        except (socket.error, pickle.PicklingError) as e:
            raise ConnectionError("Failed to send data") from e
    
    def close(self) -> None:
        print("Closing transmitter connection...")
        self.client_socket.close()