from image import Image
import numpy as np

class Jpeg:

    def __init__(self, image: Image = None) -> None:
        self.image = image
        self.image.switch_color_space("YCbCr")

    def encode(self, image: Image) -> any:
        return image

    def decode(self, dtype = np.uint8) -> Image:
       data = np.stack(self.image.get_color_spaces("RGB"), axis=-1)

       img = Image(data)
       return img