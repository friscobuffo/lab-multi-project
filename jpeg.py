import numpy as np
from image import Image
import cv2

class Jpeg:
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

    def __init__(self, image: Image) -> None:
        y, cb, cr = image.get_color_space("YCbCr")
        y = np.float32(y)
        # downsampling color
        cb = Jpeg._downsample_matrix(cb, np.float32)
        cr = Jpeg._downsample_matrix(cr, np.float32)
        # applying dct to shifted blocks
        dct_y = Jpeg._apply_dct(y - Jpeg.SHIFT, np.float32)
        dct_cb = Jpeg._apply_dct(cb - Jpeg.SHIFT, np.float32)
        dct_cr = Jpeg._apply_dct(cr - Jpeg.SHIFT, np.float32)
        # quantization
        dct_y_quantized = Jpeg._apply_quantization(dct_y, Jpeg.QUANTIZATION_MATRIX_LUMINANCE, np.int32)
        dct_cb_quantized = Jpeg._apply_quantization(dct_cb, Jpeg.QUANTIZATION_MATRIX_CROMINANCE, np.int32)
        dct_cr_quantized = Jpeg._apply_quantization(dct_cr, Jpeg.QUANTIZATION_MATRIX_CROMINANCE, np.int32)
        # zigzag view
        y_zigzags = Jpeg._apply_zigzag(dct_y_quantized, np.int32)
        cb_zigzags = Jpeg._apply_zigzag(dct_cb_quantized, np.int32)
        cr_zigzags = Jpeg._apply_zigzag(dct_cr_quantized, np.int32)
        # subtracting prev dc to next dc
        Jpeg._apply_dc_subtraction(y_zigzags)
        Jpeg._apply_dc_subtraction(cb_zigzags)
        Jpeg._apply_dc_subtraction(cr_zigzags)
        # run length encoding each block
        self.y_rle = Jpeg._apply_rle(y_zigzags, np.int8)
        self.cb_rle = Jpeg._apply_rle(cb_zigzags, np.int8)
        self.cr_rle = Jpeg._apply_rle(cr_zigzags, np.int8)
        self.original_shape = int(y.shape[0]), int(y.shape[1])

    def __init__(self, y_rle: np.ndarray, cb_rle: np.ndarray,
                 cr_rle: np.ndarray, shape: tuple[int, int]) -> None:
        self.y_rle = y_rle
        self.cb_rle = cb_rle
        self.cr_rle = cr_rle
        self.original_shape = shape

    def decode(self) -> Image:
        # inverting rle
        y_zigzags = Jpeg._apply_irle(self.y_rle, np.float32)
        cb_zigzags = Jpeg._apply_irle(self.cb_rle, np.float32)
        cr_zigzags = Jpeg._apply_irle(self.cr_rle, np.float32)
        # adding prev dc to next dc
        Jpeg._apply_dc_addition(y_zigzags)
        Jpeg._apply_dc_addition(cb_zigzags)
        Jpeg._apply_dc_addition(cr_zigzags)
        # inverting zigzag view
        color_shape = int(self.original_shape[0]/Jpeg.DOWNSAMPLE_FACTOR), int(self.original_shape[1]/Jpeg.DOWNSAMPLE_FACTOR)
        dct_y_quantized = Jpeg._apply_izigzag(y_zigzags, self.original_shape, np.float32)
        dct_cb_quantized = Jpeg._apply_izigzag(cb_zigzags, color_shape, np.float32)
        dct_cr_quantized = Jpeg._apply_izigzag(cr_zigzags, color_shape, np.float32)
        # inverting quantization
        dct_y = Jpeg._apply_dequantization(dct_y_quantized, Jpeg.QUANTIZATION_MATRIX_LUMINANCE, np.float32)
        dct_cb = Jpeg._apply_dequantization(dct_cb_quantized, Jpeg.QUANTIZATION_MATRIX_CROMINANCE, np.float32)
        dct_cr = Jpeg._apply_dequantization(dct_cr_quantized, Jpeg.QUANTIZATION_MATRIX_CROMINANCE, np.float32)
        # inverting dct and shifting
        y = np.uint8(Jpeg._apply_idct(dct_y, np.int32) + Jpeg.SHIFT)
        cb_downsampled = Jpeg._apply_idct(dct_cb, np.int32) + Jpeg.SHIFT
        cr_downsampled = Jpeg._apply_idct(dct_cr, np.int32) + Jpeg.SHIFT
        # upsampling color
        cb = Jpeg._upsample_matrix(cb_downsampled, np.uint8)
        cr = Jpeg._upsample_matrix(cr_downsampled, np.uint8)
        # rgb output
        ycbcr = np.stack((y, cb, cr), axis=-1)
        return Image(ycbcr, "YCbCr")
    
    def saveToFile(self, filename: str) -> None:
        np.savez_compressed(filename+".npz", y_rle=self.y_rle, cb_rle=self.cb_rle,
                            cr_rle=self.cr_rle, shape=self.original_shape)

    @staticmethod
    def loadFromFile(filename: str):
        data = np.load(filename + '.npz', allow_pickle=True)
        y_rle = data["y_rle"]
        cb_rle = data["cb_rle"]
        cr_rle = data["cr_rle"]
        shape = int(data["shape"][0]), int(data["shape"][1])
        return Jpeg(y_rle, cb_rle, cr_rle, shape)

    @staticmethod
    def _downsample_matrix(matrix: np.ndarray, dtype):
        size = int(matrix.shape[0]/Jpeg.DOWNSAMPLE_FACTOR), int(matrix.shape[1]/Jpeg.DOWNSAMPLE_FACTOR)
        output = np.zeros(size, dtype=dtype)
        for i in range(size[0]):
            for j in range(size[1]):
                miniblock = matrix[i*Jpeg.DOWNSAMPLE_FACTOR : i*Jpeg.DOWNSAMPLE_FACTOR+Jpeg.DOWNSAMPLE_FACTOR,
                                   j*Jpeg.DOWNSAMPLE_FACTOR : j*Jpeg.DOWNSAMPLE_FACTOR+Jpeg.DOWNSAMPLE_FACTOR]
                average = np.mean(miniblock)
                output[i,j] = average
        return output
    
    @staticmethod
    def _upsample_matrix(matrix: np.ndarray, dtype):
        size = int(matrix.shape[0]*Jpeg.DOWNSAMPLE_FACTOR), int(matrix.shape[1]*Jpeg.DOWNSAMPLE_FACTOR)
        output = np.ones(size, dtype=dtype)
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                v = matrix[i,j]
                output[i*Jpeg.DOWNSAMPLE_FACTOR : i*Jpeg.DOWNSAMPLE_FACTOR+Jpeg.DOWNSAMPLE_FACTOR,
                       j*Jpeg.DOWNSAMPLE_FACTOR : j*Jpeg.DOWNSAMPLE_FACTOR+Jpeg.DOWNSAMPLE_FACTOR] *= v
        return output
    
    @staticmethod
    def _blockproc(matrix: np.ndarray, func, dtype):
        h, w = matrix.shape
        if h % Jpeg.BLOCK_SIZE != 0 or w % Jpeg.BLOCK_SIZE != 0:
            raise ValueError("Image size must be a multiple of block size.")
        output = np.zeros_like(matrix, dtype=dtype)
        for i in range(0, h, Jpeg.BLOCK_SIZE):
            for j in range(0, w, Jpeg.BLOCK_SIZE):
                block = matrix[i:i+Jpeg.BLOCK_SIZE, j:j+Jpeg.BLOCK_SIZE]
                processed_block = func(block)
                output[i:i+Jpeg.BLOCK_SIZE, j:j+Jpeg.BLOCK_SIZE] = processed_block
        return output

    @staticmethod
    def _apply_dct(matrix: np.ndarray, dtype) -> np.ndarray:
        return Jpeg._blockproc(matrix, cv2.dct, dtype)

    @staticmethod
    def _apply_idct(matrix: np.ndarray, dtype) -> np.ndarray:
        return Jpeg._blockproc(matrix, cv2.idct, dtype)
    
    @staticmethod
    def _apply_quantization(matrix: np.ndarray, quantization_matrix: np.ndarray, dtype) -> np.ndarray:
        return Jpeg._blockproc(matrix, lambda x: x / quantization_matrix, dtype)

    @staticmethod
    def _apply_dequantization(matrix: np.ndarray, quantization_matrix: np.ndarray, dtype) -> np.ndarray:
        return Jpeg._blockproc(matrix, lambda x: x*quantization_matrix, dtype)

    @staticmethod
    def _apply_zigzag(matrix: np.ndarray, dtype):
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
            return np.array(result, dtype=dtype)
        
        if matrix.shape[0] % Jpeg.BLOCK_SIZE != 0 or matrix.shape[1] % Jpeg.BLOCK_SIZE != 0:
            raise ValueError("Image size must be a multiple of block size.")
        h = int(matrix.shape[0] / Jpeg.BLOCK_SIZE)
        w = int(matrix.shape[1] / Jpeg.BLOCK_SIZE)
        zig_zags = np.zeros((h*w, Jpeg.BLOCK_SIZE*Jpeg.BLOCK_SIZE), dtype=dtype)
        index = 0
        for i in range(h):
            for j in range(w):
                block = matrix[i*Jpeg.BLOCK_SIZE : i*Jpeg.BLOCK_SIZE+Jpeg.BLOCK_SIZE,
                               j*Jpeg.BLOCK_SIZE : j*Jpeg.BLOCK_SIZE+Jpeg.BLOCK_SIZE]
                zig_zags[index] = zigzag_traverse(block)
                index += 1
        return zig_zags

    @staticmethod
    def _apply_izigzag(zigzag_matrix: np.ndarray, matrix_shape: tuple, dtype):
        def invert_zigzag_traversal(zigzag_array: np.ndarray) -> np.ndarray:
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
        
        matrix = np.zeros(matrix_shape, dtype=dtype)
        w = matrix_shape[1] / Jpeg.BLOCK_SIZE
        i = 0
        j = 0
        for index in range(0, zigzag_matrix.shape[0]):
            matrix[i*Jpeg.BLOCK_SIZE:i*Jpeg.BLOCK_SIZE+Jpeg.BLOCK_SIZE,
                   j*Jpeg.BLOCK_SIZE:j*Jpeg.BLOCK_SIZE+Jpeg.BLOCK_SIZE] = invert_zigzag_traversal(zigzag_matrix[index])
            j += 1
            if (j==w):
                i += 1
                j = 0
        return matrix

    @staticmethod
    def _apply_dc_subtraction(matrix: np.ndarray):
        old = matrix[0,0]
        for i in range(1, matrix.shape[0]):
            temp = matrix[i,0]
            matrix[i,0] = matrix[i,0] - old
            old = temp

    @staticmethod
    def _apply_dc_addition(matrix: np.ndarray):
        for i in range(1, matrix.shape[0]):
            matrix[i,0] = matrix[i,0] + matrix[i-1,0]

    @staticmethod
    def _apply_rle(matrix: np.ndarray, dtype):
        def run_length_encoding(array: np.ndarray) -> np.ndarray:
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
        
        rle_rows = []
        for i in range(matrix.shape[0]):
            rle_rows.append(run_length_encoding(matrix[i]))
        return np.array(rle_rows, dtype=object)

    @staticmethod
    def _apply_irle(rle_rows: np.ndarray, dtype) -> np.ndarray:
        width = Jpeg.BLOCK_SIZE*Jpeg.BLOCK_SIZE
        def invert_run_length_encoding(rle: np.ndarray) -> np.ndarray:
            reconstructed = np.zeros(width, dtype=dtype)
            index = 0
            for i in range(0, len(rle), 2):
                value = rle[i]
                count = rle[i+1]
                for _ in range(count):
                    reconstructed[index] = value
                    index += 1
            return reconstructed

        matrix = np.zeros((rle_rows.shape[0], width), dtype=dtype)
        for i in range(0, rle_rows.shape[0]):
            matrix[i] = invert_run_length_encoding(rle_rows[i])
        return matrix

    def apply_vlc(frame: np.ndarray, block_size: int = None) -> np.ndarray:
        pass

    def apply_ivlc(frame: np.ndarray, block_size: int = None) -> np.ndarray:
        pass