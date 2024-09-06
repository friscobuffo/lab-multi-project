import numpy as np

from image import Image
from jpeg_ import Jpeg
from motion import MotionVector, compute_motion_compensation, compute_motion_estimation

class Encoder:
    def __init__(self, block_size: int = 8, window_size: int = 32) -> None:
        self.last_intra_frame = None
        self.last_predicted_frame = None
        self.block_size = block_size
        self.window_size = window_size
    
    def encode_intra_frame(self, frame: Image) -> Jpeg:
        encoded_frame = Jpeg(frame)
        self.last_intra_frame = encoded_frame.decode()
        return encoded_frame

    def encode_predicted_frame(self, frame: Image) -> tuple[Jpeg, list[MotionVector]]:
        mvs = compute_motion_estimation(self.last_intra_frame, frame, self.block_size, self.window_size)
        mc = compute_motion_compensation(self.last_intra_frame, mvs, self.block_size)
        encoded_mc = Jpeg(mc)

        self.last_predicted_frame = encoded_mc.decode()
        return encoded_mc, mvs

    def encode_bidirectional_frame(self, frame: Image) -> tuple[Jpeg, list[MotionVector]]:
        intra_mvs = compute_motion_estimation(self.last_intra_frame, frame, self.block_size, self.window_size)
        predicted_mvs = compute_motion_estimation(self.last_predicted_frame, frame, self.block_size, self.window_size)
        
        avg_mvs = [(intra_mv + predicted_mv) / 2 for intra_mv, predicted_mv in zip(intra_mvs, predicted_mvs)]
        
        mc = compute_motion_compensation(self.last_intra_frame, avg_mvs, self.block_size)
        encoded_mc = Jpeg(mc)

        self.last_predicted_frame = encoded_mc.decode()
        return encoded_mc, avg_mvs