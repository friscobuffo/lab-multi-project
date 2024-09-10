from video_decoder import VideoDecoder
from video_encoder_prova import VideoEncoder
import multiprocessing

# def encode():
#     encoder = VideoEncoder("test.mp4")
#     print("encoding started")
#     while (encoder.encode_next_frame()):
#         pass
#     encoder.close()

# def decode():
#     decoder = VideoDecoder()
#     print("deconding started")
#     while (decoder.process_frame()):
#         pass
#     decoder.close()

if __name__ == "__main__":
    encoder = VideoEncoder("fast_test.mp4")
    print("encoding started")
    while (encoder.encode_next_frame()):
        pass
    print("Done")
    # try:
    #     encoder_process = multiprocessing.Process(target=encode)
    #     decoder_process = multiprocessing.Process(target=decode)

    #     encoder_process.start()
    #     decoder_process.start()

    #     encoder_process.join()
    #     decoder_process.join()
        
    # except KeyboardInterrupt as e:
    #     print("Exiting...")
    #     encoder_process.terminate()
    #     decoder_process.terminate()