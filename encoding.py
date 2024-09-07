from image import Image
from jpeg import Jpeg
from motion import MotionVectors, compute_motion_compensation, compute_motion_estimation

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

    def encode_predicted_frame(self, frame: Image) -> tuple[Jpeg, MotionVectors]:
        mvs = compute_motion_estimation(self.last_intra_frame, frame, self.block_size, self.window_size)
        mc = compute_motion_compensation(self.last_intra_frame, mvs, self.block_size)
        encoded_mc = Jpeg(mc)

        self.last_predicted_frame = encoded_mc.decode()
        return encoded_mc, mvs

    def encode_bidirectional_frame(self, frame: Image) -> tuple[Jpeg, MotionVectors]:
        intra_mvs = compute_motion_estimation(self.last_intra_frame, frame, self.block_size, self.window_size)
        predicted_mvs = compute_motion_estimation(self.last_predicted_frame, frame, self.block_size, self.window_size)
        
        avg_mvs = (intra_mvs + predicted_mvs) / 2
        
        mc = compute_motion_compensation(self.last_intra_frame, avg_mvs, self.block_size)
        encoded_mc = Jpeg(mc)

        self.last_predicted_frame = encoded_mc.decode()
        return encoded_mc, avg_mvs