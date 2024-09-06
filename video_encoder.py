import numpy as np
from encoding import Encoder
from transmitter import Transmitter
from reader import VideoReader

class VideoEncoder:
    def __init__(self, path: str) -> None:
        self.path = path
        self.encoder = Encoder()
        self.transmitter = Transmitter()
        self.reader = VideoReader(path)

    def encode_video(self) -> None:
        
        num_frames = self.reader.get_total_frames()
        tmp_b1 = None
        tmp_b2 = None
        
        for i in range(num_frames):
            frame = self.reader.next_frame()
            
            # Intra Frame
            if i == 0 or (i % 9 == 0):
                intra_frame = self.encoder.encode_intra_frame(frame)
                self.transmitter.send_frame(intra_frame)
                
            # Predicted Frame - Bidirectional Frame
            elif i % 3 == 0:
                predicted_frame = self.encoder.encode_predicted_frame(frame)
                bidirectional_frame1 = self.encoder.encode_bidirectional_frame(tmp_b1)
                bidirectional_frame2 = self.encoder.encode_bidirectional_frame(tmp_b2)

                self.transmitter.send_frame(bidirectional_frame1)
                self.transmitter.send_frame(bidirectional_frame2)
                self.transmitter.send_frame(predicted_frame)
                
                tmp_b1 = None
                tmp_b2 = None
                
            else:
                if tmp_b1 is None:
                    tmp_b1 = frame
                else:
                    tmp_b2 = frame
        