import numpy as np
from encoding import Encoder
from transmitter import Transmitter
from reader import VideoReader

class VideoEncoder:
    def __init__(self) -> None:
        self.encoder = Encoder()
        self.transmitter = Transmitter()
        self.reader = VideoReader()

    def process_frame():
        pass