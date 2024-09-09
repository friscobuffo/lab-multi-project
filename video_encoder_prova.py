from encoding import Encoder
from transmitter import Transmitter
from reader import VideoReader

class VideoEncoder:
    FRAME_ORDER = ["I", "B", "B", "P", "B", "B", "P", "B", "B"]

    def __init__(self, path: str) -> None:
        self.path = path
        self.encoder = Encoder()
        self.reader = VideoReader(path)
        self.counter = 0
        self.frame_buffer = []
        self.clear_buffer = False

    def encode_next_frame(self) -> any:
        if self.counter == 0:
            self.counter += 1
            return self.encoder.encode_intra_frame(self.reader.next_frame())

        if self.clear_buffer:
            curr_frame = self.frame_buffer.pop(0)
            if len(self.frame_buffer) == 0: self.clear_buffer = False
            return self.encoder.encode_bidirectional_frame(curr_frame)
        
        index = self.counter % 9
        frame_type = VideoEncoder.FRAME_ORDER[index]
        curr_frame = self.reader.next_frame()
        if (curr_frame is None): return

        self.counter += 1
        if frame_type == "I":
            print("I")
            self.clear_buffer = True
            return self.encoder.encode_intra_frame(curr_frame)
        if frame_type == "P":
            print("P")
            self.clear_buffer = True
            return self.encoder.encode_predicted_frame(curr_frame)
        if frame_type == "B":
            print("B")
            self.frame_buffer.append(curr_frame)
            return self.encode_next_frame()




