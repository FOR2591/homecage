import threading
import numpy as np

from collections import deque
from multiprocessing import shared_memory, Queue
from typing import List

from ..frame import Frame
from .shared_frame_buffer import SharedFrameBufferReference
from .shared_frame_buffer_reader import SharedFrameBufferReader

class SharedSlidingWindowReader(SharedFrameBufferReader):
    """
    """
    def __init__(self, reference: SharedFrameBufferReference, size):
        """
        """
        super().__init__(reference=reference)
        self.idx = -1
        self.frame_count = 0
        self.window_size = size
        self.frame_buffer = deque(maxlen=self.window_size)
        self.window_queue = Queue()

        self.frame_receiver_thread = threading.Thread(target=self.receive_frame)
        self.frame_receiver_thread.daemon = True
        self.frame_receiver_thread.start()

    def get(self):
        if self.window_queue.qsize() > 0:
            return list(self.frame_buffer)
        else:
            return None

    def receive_frame(self):
        """
        """
        while True:
            if self.queue.qsize() > 0:
                signal = self.queue.get()
                frame = Frame(self.data_buffer[signal['idx']], id=signal['id'], timestamp=signal['timestamp'])

                self.frame_count += 1
                self.frame_buffer.append(frame)

                if self.frame_count >= self.window_size:
                    self.window_queue.put({})
