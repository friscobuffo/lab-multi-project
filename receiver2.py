import socket
import pickle
import struct

class Receiver:
    def __init__(self, callback) -> None:
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 9999))
        self.server_socket.listen(1)
        print("Waiting for a connection...")
        self.conn, self.addr = self.server_socket.accept()

        data = b""
        payload_size = struct.calcsize("Q")
        try:
            while True:
                while len(data) < payload_size:
                    packet = self.conn.recv(4096)
                    if not packet:
                        break
                    data += packet
                if len(data) < payload_size:
                    continue
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]
                while len(data) < msg_size:
                    packet = self.conn.recv(4096)
                    if not packet:
                        break
                    data += packet
                if len(data) < msg_size:
                    continue
                obj_data = data[:msg_size]
                data = data[msg_size:]
                obj = pickle.loads(obj_data)
                print("Received data...")
                callback(obj)
        except Exception as e:
            print(f"Error: {e}")
            print("Closing receiver connection...")
            self.conn.close()
            self.server_socket.close()
            raise e
        finally:
            print("Closing receiver connection...")
            self.conn.close()
            self.server_socket.close()