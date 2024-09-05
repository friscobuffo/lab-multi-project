import cv2
import jpeg
import matplotlib.pyplot as plt

image = cv2.imread('peppers.jpeg', cv2.IMREAD_COLOR)
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

y_rle, cb_rle, cr_rle, shape = jpeg.image2jpeg(rgb_image)
rgb = jpeg.jpeg2image(y_rle, cb_rle, cr_rle, shape)

jpeg.save_jpeg("image", y_rle, cb_rle, cr_rle, shape)

plt.imshow(rgb)
plt.axis('off')
plt.show()