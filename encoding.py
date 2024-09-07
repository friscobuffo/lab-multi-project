from image import Image
from jpeg import Jpeg
from motion import MotionVectors, compute_motion_compensation, compute_motion_estimation

class Encoder:
    def __init__(self, block_size: int = 8, window_size: int = 32) -> None:
        self.last_key_frames = []
        self.block_size = block_size
        self.window_size = window_size
    
    def encode_intra_frame(self, curr_frame: Image) -> Jpeg:
        encoded_frame = Jpeg(curr_frame)
        if self.last_key_frames:
            self.last_key_frames.pop(0)
        self.last_key_frames.append(encoded_frame.decode())
        return encoded_frame

    def encode_predicted_frame(self, curr_frame: Image) -> tuple[Jpeg, MotionVectors]:
        last_kf = self.last_key_frames[-1]
        mvs = compute_motion_estimation(last_kf, curr_frame, self.block_size, self.window_size)
        mc = compute_motion_compensation(last_kf, mvs, self.block_size)
        err = curr_frame - mc
        
        encoded_err = Jpeg(err)
        self.last_key_frames.pop(0)
        self.last_key_frames.append(encoded_err.decode() + mc)
        return encoded_err, mvs

    def encode_bidirectional_frame(self, curr_frame: Image) -> tuple[Jpeg, MotionVectors]:
        last_kf1 = self.last_key_frames[0]
        last_kf2 = self.last_key_frames[1]

        kf1_mvs = compute_motion_estimation(last_kf1, curr_frame, self.block_size, self.window_size)
        kf2_mvs = compute_motion_estimation(last_kf2, curr_frame, self.block_size, self.window_size)
        
        avg_mvs = (kf1_mvs + kf2_mvs) / 2
        mc = compute_motion_compensation(last_kf1, avg_mvs, self.block_size)
        err = curr_frame - mc
        
        encoded_err = Jpeg(err)
        return encoded_err, avg_mvs