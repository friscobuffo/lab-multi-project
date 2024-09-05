import numpy as np
import cv2

class Constants:
    DOWNSAMPLE_FACTOR = 4
    BLOCK_SIZE = 8
    SHIFT = 128
    QUANTIZATION_MATRIX_LUMINANCE = np.float32([[16,11,10,16,24,40,51,61],
                                                [12,12,14,19,26,58,60,55],
                                                [14,13,16,24,40,57,69,56],
                                                [14,17,22,29,51,87,80,62],
                                                [18,22,37,56,68,109,103,77],
                                                [24,35,55,64,81,104,113,92],
                                                [49,64,78,87,103,121,120,101],
                                                [72,92,95,98,112,100,103,99]])
    QUANTIZATION_MATRIX_CROMINANCE = np.float32([[17,18,24,47,99,99,99,99],
                                                [18,21,26,66,99,99,99,99],
                                                [24,26,56,99,99,99,99,99],
                                                [47,66,99,99,99,99,99,99],
                                                [99,99,99,99,99,99,99,99],
                                                [99,99,99,99,99,99,99,99],
                                                [99,99,99,99,99,99,99,99],
                                                [99,99,99,99,99,99,99,99]])

def blockproc(image: np.ndarray, block_size: int, func, dtype):
    h, w = image.shape
    if h % block_size != 0 or w % block_size != 0:
        raise ValueError("Image size must be a multiple of block size.")
    output = np.zeros_like(image, dtype=dtype)
    for i in range(0, h, block_size):
        for j in range(0, w, block_size):
            block = image[i:i+block_size, j:j+block_size]
            processed_block = func(block)
            output[i:i+block_size, j:j+block_size] = processed_block
    return output

def zigzag_traverse(matrix: np.ndarray, dtype) -> np.ndarray:
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
    return np.array(result, dtype=dtype)

def zigzag_block(matrix: np.ndarray, block_size: int, dtype):
    if matrix.shape[0] % block_size != 0 or matrix.shape[1] % block_size != 0:
        raise ValueError("Image size must be a multiple of block size.")
    h = int(matrix.shape[0] / block_size)
    w = int(matrix.shape[1] / block_size)
    zig_zags = np.zeros((h*w, block_size*block_size), dtype=dtype)
    index = 0
    for i in range(h):
        for j in range(w):
            block = matrix[i*block_size:i*block_size+block_size, j*block_size:j*block_size+block_size]
            zig_zags[index] = zigzag_traverse(block, dtype)
            index += 1
    return zig_zags

def run_length_encoding(array: np.ndarray, dtype) -> np.ndarray:
    if len(array) == 0:
        raise ValueError("run length encoding of empty array")
    rle = []
    current_value = array[0]
    count = 0
    for value in array:
        if value == current_value:
            count += 1
        else:
            rle.append(current_value)
            rle.append(count)
            current_value = value
            count = 1
    rle.append(current_value)
    rle.append(count)
    return dtype(rle)

def rle_matrix_rows(matrix: np.ndarray, dtype) -> np.ndarray:
    rle_rows = []
    for i in range(matrix.shape[0]):
        rle_rows.append(run_length_encoding(matrix[i], dtype))
    return np.array(rle_rows, dtype=object)

def downsample_matrix(matrix: np.ndarray, downsample_factor, dtype):
    size = int(matrix.shape[0]/downsample_factor), int(matrix.shape[1]/downsample_factor)
    output = np.zeros(size, dtype=dtype)
    for i in range(size[0]):
        for j in range(size[1]):
            miniblock = matrix[i*downsample_factor:i*downsample_factor+downsample_factor,
                               j*downsample_factor:j*downsample_factor+downsample_factor]
            average = np.mean(miniblock)
            output[i,j] = average
    return output

def image2jpeg(rgb_image: np.ndarray) -> None:
    ycbcr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2YCrCb)
    y, cb, cr = cv2.split(ycbcr_image)
    y = np.float32(y)
    # downsampling color
    cb = downsample_matrix(cb, Constants.DOWNSAMPLE_FACTOR, np.float32)
    cr = downsample_matrix(cr, Constants.DOWNSAMPLE_FACTOR, np.float32)
    # applying dct to blocks shifted
    dct_y = blockproc(y - Constants.SHIFT, Constants.BLOCK_SIZE, cv2.dct, np.float32)
    dct_cb = blockproc(cb - Constants.SHIFT, Constants.BLOCK_SIZE, cv2.dct, np.float32)
    dct_cr = blockproc(cr - Constants.SHIFT, Constants.BLOCK_SIZE, cv2.dct, np.float32)
    # quantization
    dct_y_quantized = blockproc(dct_y, Constants.BLOCK_SIZE, lambda x: x / Constants.QUANTIZATION_MATRIX_LUMINANCE, np.int32)
    dct_cb_quantized = blockproc(dct_cb, Constants.BLOCK_SIZE, lambda x: x / Constants.QUANTIZATION_MATRIX_CROMINANCE, np.int32)
    dct_cr_quantized = blockproc(dct_cr, Constants.BLOCK_SIZE, lambda x: x / Constants.QUANTIZATION_MATRIX_CROMINANCE, np.int32)
    # zigzag view
    y_zigzags = zigzag_block(dct_y_quantized, Constants.BLOCK_SIZE, np.int32)
    cb_zigzags = zigzag_block(dct_cb_quantized, Constants.BLOCK_SIZE, np.int32)
    cr_zigzags = zigzag_block(dct_cr_quantized, Constants.BLOCK_SIZE, np.int32)
    # subtracting prev dc to next dc
    old = y_zigzags[0,0]
    for i in range(1, y_zigzags.shape[0]):
        temp = y_zigzags[i,0]
        y_zigzags[i,0] = y_zigzags[i,0] - old
        old = temp
    old_cb = cb_zigzags[0,0]
    old_cr = cr_zigzags[0,0]
    for i in range(1, cb_zigzags.shape[0]):
        temp_cb = cb_zigzags[i,0]
        temp_cr = cr_zigzags[i,0]
        cb_zigzags[i,0] = cb_zigzags[i,0] - old_cb
        cr_zigzags[i,0] = cr_zigzags[i,0] - old_cr
        old_cb = temp_cb
        old_cr = temp_cr
    # run length encoding each block
    y_rle = rle_matrix_rows(y_zigzags, np.int8)
    cb_rle = rle_matrix_rows(cb_zigzags, np.int8)
    cr_rle = rle_matrix_rows(cr_zigzags, np.int8)
    return y_rle, cb_rle, cr_rle, y.shape

def save_jpeg(image_name, y_rle, cb_rle, cr_rle, shape):
    np.savez_compressed(image_name+".npz", y_rle=y_rle, cb_rle=cb_rle, cr_rle=cr_rle, shape=shape)

def invert_run_length_encoding(rle: np.ndarray, width: int, dtype) -> np.ndarray:
    reconstructed = np.zeros(width, dtype=dtype)
    index = 0
    for i in range(0, len(rle), 2):
        value = rle[i]
        count = rle[i+1]
        for _ in range(count):
            reconstructed[index] = value
            index += 1
    return reconstructed

def invert_rle_matrix_rows(rle_rows: np.ndarray, width: int, dtype) -> np.ndarray:
    matrix = np.zeros((rle_rows.shape[0], width), dtype=dtype)
    for i in range(0, rle_rows.shape[0]):
        matrix[i] = invert_run_length_encoding(rle_rows[i], width, dtype)
    return matrix

def invert_zigzag_traversal(zigzag_array: np.ndarray, dtype) -> np.ndarray:
    size = int(np.sqrt(zigzag_array.shape[0]))
    if (size*size != zigzag_array.shape[0]):
        raise ValueError("error shapes do not match")
    matrix = np.zeros((size, size), dtype=dtype)
    index = 0
    for d in range(2*size - 1):
        if d < size:
            start_row = d
            start_col = 0
        else:
            start_row = size - 1
            start_col = d - size + 1
        diag_elements = []
        row, col = start_row, start_col
        while row >= 0 and col < size:
            diag_elements.append((row, col))
            row -= 1
            col += 1
        if d % 2 == 0:
            for (r, c) in diag_elements:
                matrix[r, c] = zigzag_array[index]
                index += 1
        else:
            for (r, c) in reversed(diag_elements):
                matrix[r, c] = zigzag_array[index]
                index += 1
    return matrix

def invert_zigzag_block(zigzag_matrix: np.ndarray, matrix_shape: tuple, dtype):
    matrix = np.zeros(matrix_shape, dtype=dtype)
    w = matrix_shape[1] / Constants.BLOCK_SIZE
    i = 0
    j = 0
    for index in range(0, zigzag_matrix.shape[0]):
        matrix[i*Constants.BLOCK_SIZE:i*Constants.BLOCK_SIZE+Constants.BLOCK_SIZE,
               j*Constants.BLOCK_SIZE:j*Constants.BLOCK_SIZE+Constants.BLOCK_SIZE] = invert_zigzag_traversal(zigzag_matrix[index], dtype=dtype)
        j += 1
        if (j==w):
            i += 1
            j = 0
    return matrix

def upsample_matrix(matrix: np.ndarray, upsample_factor: int, dtype):
    size = int(matrix.shape[0]*upsample_factor), int(matrix.shape[1]*upsample_factor)
    output = np.ones(size, dtype=dtype)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = matrix[i,j]
            output[i*Constants.DOWNSAMPLE_FACTOR:i*Constants.DOWNSAMPLE_FACTOR+Constants.DOWNSAMPLE_FACTOR,
                   j*Constants.DOWNSAMPLE_FACTOR:j*Constants.DOWNSAMPLE_FACTOR+Constants.DOWNSAMPLE_FACTOR] *= v
    return output

def load_jpeg(image_name: str):
    data = np.load(image_name + '.npz', allow_pickle=True)
    y_rle = data["y_rle"]
    cb_rle = data["cb_rle"]
    cr_rle = data["cr_rle"]
    shape = int(data["shape"][0]), int(data["shape"][1])
    return y_rle, cb_rle, cr_rle, shape

def jpeg2image(y_rle, cb_rle, cr_rle, shape):
    # inverting rle
    y_zigzags = invert_rle_matrix_rows(y_rle, Constants.BLOCK_SIZE*Constants.BLOCK_SIZE, np.float32)
    cb_zigzags = invert_rle_matrix_rows(cb_rle, Constants.BLOCK_SIZE*Constants.BLOCK_SIZE, np.float32)
    cr_zigzags = invert_rle_matrix_rows(cr_rle, Constants.BLOCK_SIZE*Constants.BLOCK_SIZE, np.float32)
    # adding prev dc to next dc
    for i in range(1, y_zigzags.shape[0]):
        y_zigzags[i,0] = y_zigzags[i,0] + y_zigzags[i-1,0]
    for i in range(1, cb_zigzags.shape[0]):
        cb_zigzags[i,0] = cb_zigzags[i,0] + cb_zigzags[i-1,0]
        cr_zigzags[i,0] = cr_zigzags[i,0] + cr_zigzags[i-1,0]
    # inverting zigzag view
    color_shape = int(shape[0]/Constants.DOWNSAMPLE_FACTOR), int(shape[1]/Constants.DOWNSAMPLE_FACTOR)
    dct_y_quantized = invert_zigzag_block(y_zigzags, shape, np.float32)
    dct_cb_quantized = invert_zigzag_block(cb_zigzags, color_shape, np.float32)
    dct_cr_quantized = invert_zigzag_block(cr_zigzags, color_shape, np.float32)
    # inverting quantization
    dct_y = blockproc(dct_y_quantized, Constants.BLOCK_SIZE, lambda x: x*Constants.QUANTIZATION_MATRIX_LUMINANCE, np.float32)
    dct_cb = blockproc(dct_cb_quantized, Constants.BLOCK_SIZE, lambda x: x*Constants.QUANTIZATION_MATRIX_CROMINANCE, np.float32)
    dct_cr = blockproc(dct_cr_quantized, Constants.BLOCK_SIZE, lambda x: x*Constants.QUANTIZATION_MATRIX_CROMINANCE, np.float32)
    # shifting
    y = np.uint8(blockproc(dct_y, Constants.BLOCK_SIZE, cv2.idct, np.int32) + Constants.SHIFT)
    cb_downsampled = blockproc(dct_cb, Constants.BLOCK_SIZE, cv2.idct, np.int32) + Constants.SHIFT
    cr_downsampled = blockproc(dct_cr, Constants.BLOCK_SIZE, cv2.idct, np.int32) + Constants.SHIFT
    # upsampling color
    cb = upsample_matrix(cb_downsampled, Constants.DOWNSAMPLE_FACTOR, np.uint8)
    cr = upsample_matrix(cr_downsampled, Constants.DOWNSAMPLE_FACTOR, np.uint8)
    # rgb output
    ycbcr = np.stack((y, cb, cr), axis=-1)
    rgb_image = cv2.cvtColor(ycbcr, cv2.COLOR_YCrCb2RGB)
    return rgb_image