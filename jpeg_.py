import numpy as np
from image import Image

class Jpeg:

    def __init__(self, Image) -> None:
        pass

    def decode(self) -> Image:
        pass

    def apply_dct(frame: np.ndarray, block_size: int = None) -> np.ndarray:
        pass

    def apply_idct(frame: np.ndarray, block_size: int = None) -> np.ndarray:
        pass

    def apply_quantization(frame: np.ndarray, quantization_matrix: np.ndarray) -> np.ndarray:
        pass

    def apply_dequantization(frame: np.ndarray, quantization_matrix: np.ndarray) -> np.ndarray:
        pass

    def apply_vlc(frame: np.ndarray, block_size: int = None) -> np.ndarray:
        pass

    def apply_ivlc(frame: np.ndarray, block_size: int = None) -> np.ndarray:
        pass

    def get_dpcm():
        pass

    def get_rlc():
        pass