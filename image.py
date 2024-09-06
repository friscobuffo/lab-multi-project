import numpy as np
import cv2
import matplotlib.pyplot as plt

class Image:
    COLOR_CONVERSIONS = {
        "RGB": {
            "YCbCr": cv2.COLOR_RGB2YCrCb
        },
        "YCbCr": {
            "RGB": cv2.COLOR_YCrCb2RGB
        }
    }

    def __init__(self, image: np.ndarray, color_space: str = "RGB") -> None:
        if color_space not in self.COLOR_CONVERSIONS:
            raise ValueError(f"Unsupported color space: {color_space}")
        self.image = image
        self.color_space = color_space

    def get_color_space(self, target_space: str):
        if self.color_space == target_space:
            return self.image[:, :, 0], self.image[:, :, 1], self.image[:, :, 2]
        
        if target_space not in self.COLOR_CONVERSIONS[self.color_space]:
            raise ValueError(f"Cannot convert from {self.color_space} to {target_space}")

        image = cv2.cvtColor(self.image, self.COLOR_CONVERSIONS[self.color_space][target_space])

        return image[:, :, 0], image[:, :, 1], image[:, :, 2]
    
    def print(self):
        rgb = np.stack(self.get_color_space("RGB"), axis=-1)
        plt.imshow(rgb)
        plt.axis('off')
        plt.show()