import cv2
import jpeg_old
import matplotlib.pyplot as plt

image = cv2.imread('peppers.jpeg', cv2.IMREAD_COLOR)
rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

y_rle, cb_rle, cr_rle, shape = jpeg_old.image2jpeg(rgb_image)
rgb = jpeg_old.jpeg2image(y_rle, cb_rle, cr_rle, shape)

jpeg_old.save_jpeg("image", y_rle, cb_rle, cr_rle, shape)

plt.imshow(rgb)
plt.axis('off')
plt.show()