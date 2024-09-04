import numpy as np
import cv2
import utilities

image = cv2.imread('peppers.jpeg', cv2.IMREAD_COLOR)
ycbcr_image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)

y, cb, cr = cv2.split(ycbcr_image)

y = np.float32(y) - 128
cb = np.float32(cb[::4, ::4]) - 128
cr = np.float32(cr[::4, ::4]) - 128

dct_y = utilities.blockproc(y, (8,8), cv2.dct)
dct_cb = utilities.blockproc(cb, (8,8), cv2.dct)
dct_cr = utilities.blockproc(cr, (8,8), cv2.dct)

# idct_image_cv = cv2.idct(dct_image)

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

dct_y_quantized = utilities.blockproc(dct_y, (8, 8), lambda x: x / QUANTIZATION_MATRIX_LUMINANCE)
dct_cb_quantized = utilities.blockproc(dct_cb, (8, 8), lambda x: x / QUANTIZATION_MATRIX_CROMINANCE)
dct_cr_quantized = utilities.blockproc(dct_cr, (8, 8), lambda x: x / QUANTIZATION_MATRIX_CROMINANCE)

y_zigzags = utilities.zigzag_block(dct_y_quantized, (8,8))
cb_zigzags = utilities.zigzag_block(dct_cb_quantized, (8,8))
cr_zigzags = utilities.zigzag_block(dct_cr_quantized, (8,8))