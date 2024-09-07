import socket
import pickle

class EndOfStream:
    pass

def receive(handle_data: function, close_function: function = None) -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 12345))
    s.listen(1)
    conn, addr = s.accept()
    print('Connessione accettata da', addr)

    while True:
        data = conn.recv(1024)
        unpacked_data = pickle.loads(data)
        if (isinstance(unpacked_data, EndOfStream)):
            conn.close()
            if close_function:
                close_function()
            return
        handle_data(unpacked_data)