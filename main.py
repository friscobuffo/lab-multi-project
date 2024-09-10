from video_decoder import VideoDecoder
from video_encoder import VideoEncoder
import multiprocessing
import threading
from receiver import Receiver

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
# Funzione per avviare il Receiver

def run_receiver(receiver_container):
    receiver = Receiver()
    receiver.accept_connection()
    data = receiver.receive()
    print("Received:", data)
    receiver_container.append(receiver)
    
def close_receiver(receiver):
    receiver.close()
    print("Receiver closed")

if __name__ == "__main__":
    receiver_container = []
    receiver_thread = threading.Thread(target=run_receiver, args=(receiver_container,))
    receiver_thread.start()
    
    encoder = VideoEncoder("fast_test.mp4")
    print("encoding started")
    while (encoder.encode_next_frame()):
        pass
    
    receiver_thread.join()
    
    if receiver_container:
        close_receiver(receiver_container[0])
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