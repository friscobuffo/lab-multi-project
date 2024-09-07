import cv2
from image import Image
from jpeg import Jpeg

image = cv2.imread('peppers.jpeg', cv2.IMREAD_COLOR)
image = Image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

jpeg = Jpeg(image)
image = jpeg.decode()

image.print()