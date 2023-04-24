import numpy as np
import threading
from ...utils import logger
from multiprocessing import Queue, shared_memory

from ..frame import Frame
from .shared_frame_buffer import SharedFrameBufferReference

class SharedFrameBufferWriter():
    """
    """
    def __init__(self, reference: SharedFrameBufferReference):
        """
        """
        self.dtype = reference.dtype
        self.size = reference.size
        self.shape = reference.shape
        self.queues = reference.queues
        self.shm = shared_memory.SharedMemory(name=reference.shm_name)

        self.idx = -1
        self.data_buffer = np.ndarray((self.size, *self.shape), dtype=self.dtype, buffer=self.shm.buf)


    def put(self, frame: Frame):
        idx = self.__get_next_idx()
        if len(frame.data.shape) < 3:
            frame.data = np.expand_dims(frame.data, axis=2)
        self.data_buffer[idx, :] = frame.data
        
        for queue in self.queues:
            if queue.qsize() < self.size:
                queue.put({'idx': idx, 'id': frame.id, 'timestamp': frame.timestamp}, block=False)
            else:
                logger.info(f"Queue is full! | Size: {self.size}")

    def __get_next_idx(self):
        if self.idx + 1 < self.size:
            self.idx += 1
        else:
            self.idx = 0

        return self.idx

    def full(self):
        """
        Returns True any of the reader-queues is full
        """
        for queue in self.queues:
            if queue.qsize() >= self.size:
                return True
        return False

    def remaining(self):
        r = []
        for queue in self.queues:
            r.append(self.size - queue.qsize())
        return min(r)