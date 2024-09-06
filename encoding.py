import numpy as np
import video_utils

from image import Image
from jpeg_ import Jpeg
from motion import MotionVectors

class Encoder:
    def __init__(self) -> None:
        self.last_intra_frame = None
        self.last_predicted_frame = None
        pass
    
    def encode_intra_frame(frame: Image) -> Jpeg:
        pass

    def encode_predicted_frame(frame: Image) -> tuple[Jpeg, MotionVectors]:
        pass

    def encode_bidirectional_frame(frame: Image) -> tuple[Jpeg, MotionVectors]:
        pass

    # questa va tolta
    def process_next_frame(self, frame: np.ndarray):
        dim = frame.shape
        motions = np.zeros((dim[0]/16, dim[1]/16, 2))
        py = 0
        for i in range(0,dim[0]-15, 16):
            px = 0
            for j in range(0,dim[1]-15, 16):
                window = self.prev_frame[i:i+16, j:j+16]
                x,y = video_utils.compute_motion(frame, i, j, window, 4)
                motions[py,px,0] = x
                motions[py,px,1] = y
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