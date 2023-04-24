import cv2
import numpy as np

from collections import deque
from scipy import signal 

from core.utils import logger

class MovementTracker():

    def __init__(self, shape) -> None:
        self.shape = shape

        self.frame_buffer = deque(maxlen=5)
        self.last_frame_buffer = deque(maxlen=5)

        self.last_frame = None


    def get_movement(self, frame: np.ndarray):
        if frame.dtype == np.uint16:
            frame = np.copy(frame)
            frame = frame - np.min(frame)
            frame = frame / np.max(frame)
            frame *= 255
            frame = frame.astype(np.int8)
        elif frame.dtype == np.uint8 and len(frame.shape) == 3:
            frame = frame[:,:, 0].astype(np.int8)
        else:
            logger.warn("Incompatible itemtype")
            return 0


        if self.last_frame is not None:
            diff = np.abs(frame - self.last_frame)
            diff[diff < ( 32 )] = 0

            self.last_frame = frame
            return (np.sum(diff) / (diff.shape[0] * diff.shape[1] ))
        else:
            self.last_frame = frame
            return 0

    # def get_movement(self, img) -> float:
    #     if self.is_initialized:
    #         if img.shape[-1] == 3:
    #             img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    #         elif img.shape[-1] == 1:
    #             img_gray = np.squeeze(img)
    #         feature_points, st, err = cv2.calcOpticalFlowPyrLK(self.initial_img, img_gray, self.feature_points, None, **LK_PARAMS)

    #         return np.max(np.linalg.norm(self.feature_points - feature_points, axis=1))

    #     else:
    #         self.initialize(img)

    #         return 0



        
        