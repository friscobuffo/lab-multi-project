from video_decoder import VideoDecoder
from video_encoder import VideoEncoder

if __name__ == "__main__":
    encoder = VideoEncoder("test.mp4")
    decoder = VideoDecoder()
    while (encoder.encode_next_frame()):
        decoder.process_frame()