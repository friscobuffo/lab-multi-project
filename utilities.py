def divideMatrixByMatrix():
    pass

import numpy as np

def blockproc(image: np.ndarray, block_size: tuple, func):
    h, w = image.shape
    block_h, block_w = block_size
    
    if h % block_h != 0 or w % block_w != 0:
        raise ValueError("Image size must be a multiple of block size.")
    output = np.zeros_like(image, dtype=np.float32)
    for i in range(0, h, block_h):
        for j in range(0, w, block_w):
            block = image[i:i+block_h, j:j+block_w]
            processed_block = func(block)
            output[i:i+block_h, j:j+block_w] = processed_block
    
    return output
