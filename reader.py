import cv2 as cv

from image import Image

class VideoReader:
    def __init__(self, path: str) -> None:
        self.path= path
        self.video = cv.VideoCapture(self.path)
    
    def next_frame(self) -> Image:
        state, frame = self.video.read()
        if not state:
            return None
        return Image(frame)