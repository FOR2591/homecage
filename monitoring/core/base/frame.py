import time
import numpy as np

class Frame:
    """
    Class for representing a single video frame.

    """

    def __init__(self, data, id, timestamp=time.time()):
        self.data: np.ndarray = data
        self.id = id
        self.width = self.data.shape[0]
        self.height = self.data.shape[1]
        self.timestamp: float = timestamp

        self.has_rgb = False
        self.has_gray = False
