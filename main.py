from video_decoder import VideoDecoder
from video_encoder_prova import VideoEncoder
import multiprocessing

def encode():
    encoder = VideoEncoder("fast_test.mp4")
    print("Encoding started...")
    while (encoder.send_next_frame()):
        pass
    encoder.close()

def decode():
    VideoDecoder()

if __name__ == "__main__":
    try:
        encoder_process = multiprocessing.Process(target=encode)
        decoder_process = multiprocessing.Process(target=decode)

        encoder_process.start()
        decoder_process.start()

        encoder_process.join()
        decoder_process.join()
        
    except KeyboardInterrupt as e:
        print("Exiting...")
        encoder_process.terminate()
        decoder_process.terminate()