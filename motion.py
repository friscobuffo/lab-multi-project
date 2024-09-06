from numpy import np
from image import Image

class MotionVectors:

    def __init__(self, prev_frame: Image, next_frame: Image) -> None:
        self.vectors = None

    def compute_motion_estimation():
        pass

    def compute_motion_compensation():
        pass

    def matrices_distance(matrix1: np.ndarray, matrix2: np.ndarray) -> int:
        return np.sum(np.abs(matrix1-matrix2))

    def compute_motion(image: np.ndarray, window_x, window_y, window: np.ndarray, max_slide: int):
        window_size = window.shape
        dim = image.shape
        best = (window_x, window_y)
        best_value = matrices_distance(image[window_x:window_x+window_size[0],
                                            window_y:window_y+window_size[1]], window)
        for i in range(window_x-max_slide, window_x+max_slide+1):
            if i < 0 or i+window_size[0] >= dim[0]:
                continue
            for j in range(window_y-max_slide, window_y+max_slide+1):
                if j < 0 or j+window_size[1] >= dim[1]:
                    continue
                curr_value = matrices_distance(image[i:i+window_size[0], j:j+window_size[1]], window)
                if curr_value<best_value:
                    best_value = curr_value
                    best = (i, j)
        motion_x = best[0] - window_x
        motion_y = best[1] - window_y
        return motion_x, motion_y