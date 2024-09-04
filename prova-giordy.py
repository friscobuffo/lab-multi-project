import numpy as np
import cv2
import utilities

image = cv2.imread('peppers.jpeg', cv2.IMREAD_COLOR)
ycbcr_image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)

Y, Cb, Cr = cv2.split(ycbcr_image)

Y = np.float32(Y)
Cb = np.float32(Cb[::4, ::4])
Cr = np.float32(Cr[::4, ::4])

dct_Y = utilities.blockproc(Y, (8,8), cv2.dct)
dct_Cb = utilities.blockproc(Cb, (8,8), cv2.dct)
dct_Cr = utilities.blockproc(Cr, (8,8), cv2.dct)

exit(1)

idct_image_cv = cv2.idct(dct_image)

quantization_matrix_luminance = [[16,11,10,16,24,40,51,61],
                                [12,12,14,19,26,58,60,55],
                                [14,13,16,24,40,57,69,56],
                                [14,17,22,29,51,87,80,62],
                                [18,22,37,56,68,109,103,77],
                                [24,35,55,64,81,104,113,92],
                                [49,64,78,87,103,121,120,101],
                                [72,92,95,98,112,100,103,99]]

quantization_matrix_crominance = [[17,18,24,47,99,99,99,99],
                                [18,21,26,66,99,99,99,99],
                                [24,26,56,99,99,99,99,99],
                                [47,66,99,99,99,99,99,99],
                                [99,99,99,99,99,99,99,99],
                                [99,99,99,99,99,99,99,99],
                                [99,99,99,99,99,99,99,99],
                                [99,99,99,99,99,99,99,99]]