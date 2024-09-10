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

    def get_color_spaces(self, target_space: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if self.color_space == target_space:
            return self.image[:, :, 0], self.image[:, :, 1], self.image[:, :, 2]
        
        if target_space not in Image.COLOR_CONVERSIONS[self.color_space]:
            raise ValueError(f"Cannot convert from {self.color_space} to {target_space}")

        image = cv2.cvtColor(self.image, Image.COLOR_CONVERSIONS[self.color_space][target_space])

        return image[:, :, 0], image[:, :, 1], image[:, :, 2]

    def switch_color_space(self, target_space: str) -> None:
        if self.color_space == target_space:
            return

        if target_space not in Image.COLOR_CONVERSIONS[self.color_space]:
            raise ValueError(f"Cannot convert from {self.color_space} to {target_space}")
        
        if self.color_space != target_space:
            self.image = cv2.cvtColor(self.image, Image.COLOR_CONVERSIONS[self.color_space][target_space])
            self.color_space = target_space
    
    def print(self) -> None:
        rgb = np.stack(self.get_color_spaces("RGB"), axis=-1)

        def on_key(event):
            print(f"Key pressed: {event.key}")
            plt.close()

        fig, ax = plt.subplots()
        ax.imshow(rgb)
        ax.axis('off')

        fig.canvas.mpl_connect('key_press_event', on_key)

        plt.show()


    def __add__(self, other: 'Image') -> 'Image':
        if self.color_space != other.color_space:
            raise ValueError("Images must have the same color space.")

        summed_image = self.image + other.image
        return Image(summed_image, color_space=self.color_space)
    
    def __sub__(self, other: 'Image') -> 'Image':
        if self.color_space != other.color_space:
            raise ValueError("Images must have the same color space.")

        subtracted_image = self.image - other.image
        return Image(subtracted_image, color_space=self.color_space)