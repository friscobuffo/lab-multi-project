import cv2 as cv

from image import Image

class VideoReader:
    def __init__(self, path: str) -> None:
        
        self.path= path
        self.frames = []
        self.video = self.load_video(path)
        self.current_frame = 0
    
    def next_frame(self) -> Image:
        frame = self.frames[self.current_frame]
        self.current_frame += 1
        return Image(frame)
    
    def load_video(self):
        self.video = cv.VideoCapture(self.path)
        self.extract_frames()
    
    def extract_frames(self):
        while True:
            state, frame = self.video.read()
            if not state:
                break
            self.frames.append(frame)
            
    def get_total_frames(self):
        return len(self.frames)
            
            
        