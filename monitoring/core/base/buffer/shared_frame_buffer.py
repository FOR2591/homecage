import numpy as np

from typing import List
from multiprocessing import Queue, shared_memory

def nbytes(shape: np.ndarray, dtype: np.dtype):
    nbytes = np.dtype(dtype).itemsize

    for s in shape:
        nbytes *= s

    return nbytes

class SharedFrameBufferReference():
    """
    Class for a reference from which a local SharedFrameBuffer object can be created
    """
    def __init__(self, shape, queues: List[Queue], shm_name: str, size=10, dtype=np.uint8):
        self.dtype = dtype
        self.size = size
        self.shape = shape
        self.queues = queues
        self.shm_name = shm_name

class SharedFrameBuffer():
    """
    """
    def __init__(self, shape, size=10, dtype=np.uint8):
        """
        """
        self.shape = shape
        self.size = size
        self.dtype = dtype
        self.queues : List[Queue]  = []
        self.shm_reader_refs = []
        self.shm_writer_refs = []
        self.shm = shared_memory.SharedMemory(create=True, size=nbytes((size, *shape), dtype))


    def get_reference(self, mode: str) -> SharedFrameBufferReference:
        """
        """
        if mode == 'r':
            queue = Queue()
            shm_ref = SharedFrameBufferReference(shape = self.shape, queues=[queue], size=self.size, dtype=self.dtype, shm_name = self.shm.name)

            self.queues.append(queue)
            self.shm_reader_refs.append(shm_ref)

            # No need for writer queue update, as self.queues is referenced by "pointer"
            # # update writer queues
            # for writer_ref in self.shm_writer_refs:
            #     writer_ref.queues.append(queue)

        else: # mode == 'w
            shm_ref = SharedFrameBufferReference(shape = self.shape, queues=self.queues, size=self.size, dtype=self.dtype, shm_name = self.shm.name)
            self.shm_writer_refs.append(shm_ref)

        return shm_ref

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
    
