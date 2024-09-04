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

import numpy as np

def zigzag_traverse(matrix: np.ndarray) -> np.ndarray:
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("matrix must be square")
    n = matrix.shape[0]
    result = []
    
    for d in range(2 * n - 1):
        if d < n:
            start_row = d
            start_col = 0
        else:
            start_row = n - 1
            start_col = d - n + 1

        diag_elements = []
        row, col = start_row, start_col
        while row >= 0 and col < n:
            diag_elements.append(matrix[row, col])
            row -= 1
            col += 1

        if d % 2 == 0:
            result.extend(diag_elements)
        else:
            result.extend(diag_elements[::-1])

    return np.array(result)

def zigzag_block(matrix: np.ndarray, block_size: tuple):
    block_h, block_w = block_size
    
    if matrix.shape[0] % block_h != 0 or matrix.shape[1] % block_w != 0:
        raise ValueError("Image size must be a multiple of block size.")
    
    h = int(matrix.shape[0] / 8)
    w = int(matrix.shape[1] / 8)

    zig_zags = np.zeros((h*w, 64))
    index = 0
    for i in range(0, h):
        for j in range(0, w):
            block = matrix[i*8:i*8+8, j*8:j*8+8]
            zig_zags[index] = zigzag_traverse(block)
            index += 1

    return zig_zags