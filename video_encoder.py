from encoding import Encoder
from transmitter import Transmitter
from reader import VideoReader

class VideoEncoder:
    def __init__(self, path: str) -> None:
        self.path = path
        self.encoder = Encoder()
        self.transmitter = Transmitter()
        self.reader = VideoReader(path)
        self.buffer_last_10_frames = []
        self.buffer_to_send = []

    def encode_next_frame(self) -> bool:
        if (len(self.buffer_to_send) > 0):
            self.transmitter.send(self.buffer_to_send.pop(0))
            return True
        self.populate_buffer_to_send()
        if (len(self.buffer_to_send) == 0):
            return False
        self.encode_next_frame()

    def last_frames_of_video(self):
        if (len(self.buffer_last_10_frames) == 0):
            return
        self.buffer_last_10_frames.pop(0)
        while (len(self.buffer_last_10_frames)):
            frame = self.buffer_last_10_frames.pop(0)
            intra_frame = self.encoder.encode_intra_frame(frame)
            self.buffer_to_send.append((intra_frame, None))

    def populate_buffer_to_send(self) -> None:
        send_first_intra = (len(self.buffer_last_10_frames) == 0)
        while (len(self.buffer_last_10_frames) < 10):
            frame = self.reader.next_frame()
            if (frame is None):
                return self.last_frames_of_video()
            self.buffer_last_10_frames.append(frame)
        # Intra Frame 1
        if (send_first_intra):
            intra_frame_0 = self.encoder.encode_intra_frame(self.buffer_last_10_frames[0])
            self.buffer_to_send.append((intra_frame_0, None))
        # Predicted Frame - Bidirectional Frame (block 1)
        error_pf_3, motion_vectors_pf_3 = self.encoder.encode_predicted_frame(self.buffer_last_10_frames[3])
        error_bf_1, motion_vectors_bd_1 = self.encoder.encode_bidirectional_frame(self.buffer_last_10_frames[1])
        error_bf_2, motion_vectors_bd_2 = self.encoder.encode_bidirectional_frame(self.buffer_last_10_frames[2])
        # Predicted Frame - Bidirectional Frame (block 2)
        error_pf_6, motion_vectors_pf_6 = self.encoder.encode_predicted_frame(self.buffer_last_10_frames[6])
        error_bf_4, motion_vectors_bd_4 = self.encoder.encode_bidirectional_frame(self.buffer_last_10_frames[4])
        error_bf_5, motion_vectors_bd_5 = self.encoder.encode_bidirectional_frame(self.buffer_last_10_frames[5])
        # Intra Frame 2
        intra_frame_9 = self.encoder.encode_intra_frame(self.buffer_last_10_frames[9])
        # Bidirectional Frame (block 3)
        bidirectional_frame_7, motion_vectors_bd_7 = self.encoder.encode_bidirectional_frame(self.buffer_last_10_frames[7])
        bidirectional_frame_8, motion_vectors_bd_8 = self.encoder.encode_bidirectional_frame(self.buffer_last_10_frames[8])
        # Populating buffer to send
        self.buffer_to_send.append((error_bf_1, motion_vectors_bd_1))
        self.buffer_to_send.append((error_bf_2, motion_vectors_bd_2))
        self.buffer_to_send.append((error_pf_3, motion_vectors_pf_3))
        self.buffer_to_send.append((error_bf_4, motion_vectors_bd_4))
        self.buffer_to_send.append((error_bf_5, motion_vectors_bd_5))
        self.buffer_to_send.append((error_pf_6, motion_vectors_pf_6))
        self.buffer_to_send.append((bidirectional_frame_7, motion_vectors_bd_7))
        self.buffer_to_send.append((bidirectional_frame_8, motion_vectors_bd_8))
        self.buffer_to_send.append((intra_frame_9, None))

        self.buffer_last_10_frames = [self.buffer_last_10_frames[9]]