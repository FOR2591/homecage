import threading
import numpy as np

from typing import List
from multiprocessing import shared_memory, Queue

from ..frame import Frame
from .shared_frame_buffer import SharedFrameBufferReference

class SharedFrameBufferReader:
    """
    """
    def __init__(self, reference: SharedFrameBufferReference):
        """
        """

        self.dtype = reference.dtype
        self.size = reference.size
        self.shape = reference.shape
        self.queue = reference.queues[0]
        self.shm = shared_memory.SharedMemory(name=reference.shm_name)
        self.data_buffer = np.ndarray((self.size, *self.shape), dtype=self.dtype, buffer=self.shm.buf)

    def get(self, blocking=False) -> Frame:
        if self.queue.qsize() > 0 or blocking:
            signal = self.queue.get()
            frame = Frame(self.data_buffer[signal['idx']], id=signal['id'], timestamp=signal['timestamp'])
            return frame
        else:
            return None

    @property
    def remaining(self):
        return self.size - self.queue.qsize()

    # @property
    # def on_frame(self):
    #     return self.on_frame  

    # @on_frame.setter
    # def on_frame(self, callback):
    #     self.__on_frame.subscribe(on_next=callback)

    # def __frame_listener(self): 
    #     while True:
    #         if self.queues[0].qsize() > self.size:
    #             print('BUFFEROVERFLOW')

    #         signal = self.queues[0].get()
    #         frame = Frame(self.data_buffer[signal['idx']], id=signal['id'], timestamp=signal['timestamp'])
    #         self.__on_frame.on_next(frame)
