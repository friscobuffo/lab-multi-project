from encoding import Encoder
from transmitter import Transmitter
from reader import VideoReader

class VideoEncoder:
    FRAME_ORDER = ["I", "B", "B", "P", "B", "B", "P", "B", "B"]

    def __init__(self, path: str) -> None:
        self.path = path
        self.encoder = Encoder()
        self.reader = VideoReader(path)
        self.transmitter = Transmitter()
        self.frame_counter = 0
        self.frame_buffer = []
        self.clear_buffer = False
        self.send_buffer = []

    def encode_next_frame(self) -> any:
        if self.frame_counter == 0:
            self.frame_counter += 1
            return self.encoder.encode_intra_frame(self.reader.next_frame()), None, "I"

        if self.clear_buffer:
            curr_frame = self.frame_buffer.pop(0)
            if len(self.frame_buffer) == 0: self.clear_buffer = False
            err, mvs = self.encoder.encode_bidirectional_frame(curr_frame)
            return err, mvs, "B"
        
        index = self.frame_counter % 9
        frame_type = VideoEncoder.FRAME_ORDER[index]
        curr_frame = self.reader.next_frame()
        if (curr_frame is None): return None

        self.frame_counter += 1
        if frame_type == "I":
            self.clear_buffer = True
            return self.encoder.encode_intra_frame(curr_frame), None, "I"
        if frame_type == "P":
            self.clear_buffer = True
            err, mvs = self.encoder.encode_predicted_frame(curr_frame)
            return err, mvs, "P"
        if frame_type == "B":
            self.frame_buffer.append(curr_frame)
            return self.encode_next_frame()
        
    def send_next_frame(self) -> None:
        data = self.encode_next_frame()
        if data == None: return False

        if data[2] != "B":
            self.send_buffer.append(data)
            if len(self.send_buffer) != 0:
                print("sending key frame")
                self.transmitter.send(self.send_buffer.pop(0))
                return True
            else:
                return self.send_next_frame()
        else:
            print("sending bidirectional frame")
            self.transmitter.send(data)
            return True

    def close(self) -> None:
        self.transmitter.send(None)
        self.transmitter.close()