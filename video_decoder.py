import numpy as np
from decoding import Decoder
from receiver import Receiver

class VideoDecoder:
    def __init__(self) -> None:
        self.decoder = Decoder()
        self.receiver = Receiver()

    def process_frame(self) -> None:
        self.receiver.receive()