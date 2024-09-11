import cv2
from image import Image
from jpeg import Jpeg
import pickle
from compresser import Compresser

image = cv2.imread('peppers.jpeg', cv2.IMREAD_COLOR)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

width = image.shape[0]
height = image.shape[1]
channels = image.shape[2]

total_bytes = width * height * channels

image = Image(image)

jpeg = Jpeg(image)

show_image = False
if show_image:
    image = jpeg.decode()
    image.print(False)

serialized = pickle.dumps(jpeg)
compresser = Compresser()
serialized_compressed = compresser.compress(serialized)

print(f"Raw image size: {total_bytes} bytes.")
print(f"Compressed image size: {len(serialized_compressed)} bytes.")
print(f"Compression ratio: {total_bytes/len(serialized_compressed):.2f}")