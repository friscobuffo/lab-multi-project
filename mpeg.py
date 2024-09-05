import numpy as np

def matrices_distance(matrix1: np.ndarray, matrix2: np.ndarray) -> int:
    return np.sum(np.abs(matrix1-matrix2))

def compute_motion(image: np.ndarray, window_x, window_y, window: np.ndarray, max_slide: int):
    window_size = window.shape
    dim = image.shape
    best = (window_x, window_y)
    best_value = matrices_distance(image[window_x:window_x+window_size[0],
                                         window_y:window_y+window_size[1]], window)
    for i in range(window_x-max_slide, window_x+max_slide+1):
        if i<0 or i+window_size[0]>=dim[0]:
            continue
        for j in range(window_y-max_slide, window_y+max_slide+1):
            if j<0 or j+window_size[1]>=dim[1]:
                continue
            curr_value = matrices_distance(image[i:i+window_size[0], j:j+window_size[1]], window)
            if curr_value<best_value:
                best_value = curr_value
                best = (i, j)
    motion_x = best[0] - window_x
    motion_y = best[1] - window_y
    return motion_x, motion_y

class VideoCompresser:
    def __init__(self, first_frame: np.ndarray) -> None:
        self.prev_frame = first_frame
    
    def process_next_frame(self, frame: np.ndarray):
        dim = frame.shape
        motions = np.zeros((dim[0]/16, dim[1]/16, 2))
        py = 0
        for i in range(0,dim[0]-15, 16):
            px = 0
            for j in range(0,dim[1]-15, 16):
                window = self.prev_frame[i:i+16, j:j+16]
                x,y = compute_motion(frame, i, j, window, 4)
                motions[px,py,0] = x
                motions[px,py,1] = y
                px += 1
            py += 1
        self.prev_frame = frame


# ricostruire
# result = zeros(size(frame1));
# for i = 1:16:dim(1)-15
#     for j = 1:16:dim(2)-15
#         window = frame1(i:i+15, j:j+15);
#         [x,y] = compareWindow(frame2, i, j, window);
#         result(i+x:i+x+15, j+y:j+y+15) = window;
#     end
# end