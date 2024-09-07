import numpy as np
from image import Image

class MotionVector:
    def __init__(self, start: tuple[int, int], end: tuple[int, int]) -> None:
        self.start = np.array(start, dtype=np.int32)
        self.end = np.array(end, dtype=np.int32)
        self.vector = self.end - self.start

    def __add__(self, other: 'MotionVector') -> 'MotionVector':
        if not isinstance(other, MotionVector):
            return ValueError
        
        new_start = self.start + other.vector
        new_end = self.end + other.vector
        return MotionVector(tuple(new_start), tuple(new_end))

    def __sub__(self, other: 'MotionVector') -> 'MotionVector':
        if not isinstance(other, MotionVector):
            return ValueError
        
        new_start = self.start - other.vector
        new_end = self.end - other.vector
        return MotionVector(tuple(new_start), tuple(new_end))
    
    def __mul__(self, scalar: float) -> 'MotionVector':
        if not isinstance(scalar, (int, float)):
            return ValueError
        
        new_start = self.start * scalar
        new_end = self.end * scalar
        return MotionVector(tuple(new_start.astype(int)), tuple(new_end.astype(int)))

    def __truediv__(self, scalar: float) -> 'MotionVector':
        if not isinstance(scalar, (int, float)) or scalar == 0:
            return ValueError
        
        new_start = self.start / scalar
        new_end = self.end / scalar
        return MotionVector(tuple(new_start.astype(int)), tuple(new_end.astype(int)))


def compute_motion_estimation(prev_frame: Image, next_frame: Image, block_size: int, window_size: int) -> list[MotionVector]:
    prev_Y, next_Y = prev_frame.get_color_space("YCbCr")[0], next_frame.get_color_space("YCbCr")[0]
    height, width = prev_Y.shape
    motion_vectors = []

    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            current_block = next_Y[i:i+block_size, j:j+block_size]

            x_start = max(0, i - window_size)
            y_start = max(0, j - window_size)
            x_end = min(height - block_size, i + window_size)
            y_end = min(width - block_size, j + window_size)

            min_sad = float('inf')
            best_match = (i, j) 
            
            for x in range(x_start, x_end + 1):
                for y in range(y_start, y_end + 1):
                    candidate_block = prev_Y[x:x + block_size, y:y + block_size]
                    sad = np.sum(np.abs(current_block - candidate_block))

                    if sad < min_sad:
                        min_sad = sad
                        best_match = (x, y)

            motion_vectors.append(MotionVector((i, j), best_match))
    
    return motion_vectors


def compute_motion_compensation(prev_frame: Image, mvs: list[MotionVector], block_size: int) -> Image:
    prev_Y, prev_Cb, prev_Cr = prev_frame.get_color_space("YCbCr")
    compensated_Y = np.zeros_like(prev_Y)

    for mv in mvs:
        prev_x, prev_y = mv.start
        mv_x, mv_y = mv.vector

        ref_x = prev_x + mv_x
        ref_y = prev_y + mv_y

        compensated_Y[prev_x:prev_x+block_size, prev_y:prev_y+block_size] = prev_Y[ref_x:ref_x+block_size, ref_y:ref_y+block_size]

    image_YCbCr = np.stack((compensated_Y, prev_Cb, prev_Cr), axis=-1)
    return Image(image_YCbCr, "YCbCr")
