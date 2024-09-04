import cv2
import jpeg
import numpy as np
import matplotlib.pyplot as plt

image = cv2.imread('peppers.jpeg', cv2.IMREAD_COLOR)
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

jpeg.image2jpeg("image", rgb_image)

r,g,b = jpeg.jpeg2image("image")
rgb_image = np.stack((r, g, b), axis=-1)

plt.imshow(rgb_image)
plt.axis('off')
plt.show()