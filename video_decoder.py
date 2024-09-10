from decoding import Decoder
from receiver2 import Receiver

class VideoDecoder:
    def __init__(self) -> None:
        self.decoder = Decoder()
        self.frame_counter = 0
        self.receiver = Receiver(self.process_frame)

    def process_frame(self, data) -> bool:
        error, motion = data
        print("Processing frame...")
        if self.frame_counter == 0:
            self.decoder.decode_intra_frame(error)
        elif self.frame_counter < 3:
            self.decoder.decode_bidirectional_frame(error, motion)
        elif self.frame_counter == 4:
            self.decoder.decode_predicted_frame(error, motion)
        elif self.frame_counter < 7:
            self.decoder.decode_bidirectional_frame(error, motion)
        elif self.frame_counter == 7:
            self.decoder.decode_predicted_frame(error, motion)
        elif self.frame_counter < 10:
            self.decoder.decode_bidirectional_frame(error, motion)
        else:
            self.decoder.decode_intra_frame(error)
            self.frame_counter = 0
        
        self.frame_counter += 1