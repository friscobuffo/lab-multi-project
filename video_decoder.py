import numpy as np
from decoding import Decoder
from receiver import Receiver

class VideoDecoder:
    def __init__(self) -> None:
        self.decoder = Decoder()
        self.receiver = Receiver()
        self.frame_counter = 0

    def process_frame(self) -> bool:
        error, motion = self.receiver.receive()
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
        return True
    
    def close(self) -> None:
        self.receiver.close()