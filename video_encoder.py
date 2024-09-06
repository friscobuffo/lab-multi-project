import numpy as np
from encoding import Encoder
from transmitter import Transmitter
from reader import VideoReader

class VideoEncoder:
    def __init__(self) -> None:
        self.encoder = Encoder()
        self.transmitter = Transmitter()
        self.reader = VideoReader()

    def encode_video(path: str) -> None:
        tmp_b1 = None
        tmp_b2 = None

    def process_frame():
        pass