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
        if color_space not in Image.COLOR_CONVERSIONS:
            raise ValueError(f"Unsupported color space: {color_space}")
        self.image = image
        self.color_space = color_space

    def get_color_space(self, target_space: str):
        if self.color_space == target_space:
            return self.image[:, :, 0], self.image[:, :, 1], self.image[:, :, 2]
        
        if target_space not in Image.COLOR_CONVERSIONS[self.color_space]:
            raise ValueError(f"Cannot convert from {self.color_space} to {target_space}")

        image = cv2.cvtColor(self.image, Image.COLOR_CONVERSIONS[self.color_space][target_space])

        return image[:, :, 0], image[:, :, 1], image[:, :, 2]
    
    def print(self):
        rgb = np.stack(self.get_color_space("RGB"), axis=-1)
        plt.imshow(rgb)
        plt.axis('off')
        plt.show()

    def __add__(self, other: 'Image') -> 'Image':
        if self.color_space != other.color_space:
            other_image_converted = other.convert_color_space(self.color_space)
        else:
            other_image_converted = other.image
            
        if self.image.shape != other_image_converted.shape:
            raise ValueError("Images must have the same dimensions to be added.")

        summed_image = np.clip(self.image + other_image_converted, 0, 255).astype(np.uint8)
        return Image(summed_image, color_space=self.color_space)
    
    def __sub__(self, other: 'Image') -> 'Image':
        if self.color_space != other.color_space:
            other_image_converted = other.convert_color_space(self.color_space)
        else:
            other_image_converted = other.image

        if self.image.shape != other_image_converted.shape:
            raise ValueError("Images must have the same dimensions to be subtracted.")

        subtracted_image = np.clip(self.image - other_image_converted, 0, 255).astype(np.uint8)
        return Image(subtracted_image, color_space=self.color_space)