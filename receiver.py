# import socket
# import pickle
# import struct

# class Receiver:
#     def __init__(self, callback) -> None:
#         self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server_socket.bind(('localhost', 9999))
#         self.server_socket.listen(1)
#         print("Waiting for a connection...")
#         self.conn, self.addr = self.server_socket.accept()

#         data = b""
#         payload_size = struct.calcsize("Q")
#         try:
#             while True:
#                 while len(data) < payload_size:
#                     packet = self.conn.recv(4096)
#                     if not packet:
#                         break
#                     data += packet
#                 if len(data) < payload_size:
#                     continue
#                 packed_msg_size = data[:payload_size]
#                 data = data[payload_size:]
#                 msg_size = struct.unpack("Q", packed_msg_size)[0]
#                 while len(data) < msg_size:
#                     packet = self.conn.recv(4096)
#                     if not packet:
#                         break
#                     data += packet
#                 if len(data) < msg_size:
#                     continue
#                 obj_data = data[:msg_size]
#                 data = data[msg_size:]
#                 obj = pickle.loads(obj_data)
#                 if data is None:
#                     print("Finished receiving...")
#                     break
#                 print("Received data...")
#                 callback(obj)
#         except Exception as e:
#             print(f"Error: {e}")
#             print("Closing receiver connection...")
#             self.conn.close()
#             self.server_socket.close()
#             raise e
#         finally:
#             print("Closing receiver connection...")
#             self.conn.close()
#             self.server_socket.close()

import socket
import struct
import pickle

class Receiver:
    def __init__(self, callback) -> None:
        self.callback = callback
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 9999))
        self.server_socket.listen(1)
        print("Waiting for a connection...")
        try:
            self.conn, self.addr = self.server_socket.accept()
            print(f"Connection established with {self.addr}")
            self.receive_data()
        except Exception as e:
            print(f"Error during connection setup: {e}")
            self.close()

    def receive_data(self):
        data = b""
        payload_size = struct.calcsize("Q")
        try:
            while True:
                # Ensure we have enough data to determine message size
                while len(data) < payload_size:
                    packet = self.conn.recv(4096)
                    if not packet:
                        print("Connection closed by the client.")
                        return
                    data += packet

                # Extract the message size
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                # Receive the actual message based on the size
                while len(data) < msg_size:
                    packet = self.conn.recv(4096)
                    if not packet:
                        print("Connection closed during message reception.")
                        return
                    data += packet

                obj_data = data[:msg_size]
                data = data[msg_size:]
                obj = pickle.loads(obj_data)
                self.callback(obj)
        except Exception as e:
            print(f"Error while receiving data: {e}")
        finally:
            self.close()

    def close(self):
        print("Closing receiver connection...")
        try:
            if self.conn:
                self.conn.close()
            if self.server_socket:
                self.server_socket.close()
        except Exception as e:
            print(f"Error while closing connection: {e}")

    def __exit__(self):
        self.close()
        
