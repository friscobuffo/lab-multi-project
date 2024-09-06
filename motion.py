import numpy as np

from image import Image

class MotionVectors:

    def __init__(self, prev_frame: Image, next_frame: Image, block_size: int, window_size: int) -> None:
        height, width = prev_frame.get_color_space("YCbCr")[0].shape
        if width % block_size != 0 or height % block_size != 0:
            raise ValueError("Image size must be a multiple of block size.")

        self.block_size = block_size
        self.window_size = window_size
        self.motion_vectors = None
        self._compute_motion_estimation(prev_frame, next_frame)

    def _compute_motion_estimation(self, prev_frame: Image, next_frame: Image):
        prev_Y, next_Y = prev_frame.get_color_space("YCbCr")[0], next_frame.get_color_space("YCbCr")[0]

        height, width = prev_Y.shape
        motion_vectors = []

        for i in range(0, height, self.block_size):
            for j in range(0, width, self.block_size):
                current_block = next_Y[i:i+self.block_size, j:j+self.block_size]

                x_start = max(0, i - self.window_size)
                y_start = max(0, j - self.window_size)
                x_end = min(height - self.block_size, i + self.window_size)
                y_end = min(width - self.block_size, j + self.window_size)

                min_sad = float('inf')
                best_match = (0, 0)
                for x in range(x_start, x_end - self.block_size + 1):
                    for y in range(y_start, y_end - self.block_size + 1):
                        candidate_block = prev_Y[x:x + self.block_size, y:y + self.block_size]

                        sad = np.sum(np.abs(current_block - candidate_block))

                        if sad < min_sad:
                            min_sad = sad
                            best_match = (x - i, y - j)

                motion_vectors.append(((i, j), best_match))
        
        self.motion_vectors = motion_vectors


    def compute_motion_compensation(self, prev_frame: Image) -> np.ndarray:
        prev_Y, prev_Cb, prev_Cr = prev_frame.get_color_space("YCbCr")
        compensated_Y = np.zeros_like(prev_Y)

        for (block_pos, motion_vector) in self.motion_vectors:
            x, y = block_pos
            mv_x, mv_y = motion_vector

            ref_x = x + mv_x
            ref_y = y + mv_y

            compensated_Y[x:x+self.block_size, y:y+self.block_size] = prev_Y[ref_x:ref_x+self.block_size, ref_y:ref_y+self.block_size]

        image_YCbCr = np.stack((compensated_Y, prev_Cb, prev_Cr), axis=-1)
        return Image(image_YCbCr, "YCbCr")