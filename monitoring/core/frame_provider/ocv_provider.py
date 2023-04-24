import cv2
import time
import threading

import numpy as np

from ..utils import logger
from ..base import Frame, FrameProvider
from ..base.buffer import SharedFrameBuffer 

class OCVProvider(FrameProvider):   
    """
    OpenCV Video Provider for live camera input
    """
    
    def __init__(self, buffer: SharedFrameBuffer, device_id = 0):
        super().__init__()
        self.buffer = buffer
        self.device_id = device_id
        
        self.capture_device: cv2.VideoCapture = None

    def connect(self) -> bool:
        """
        Connect to camera
        """
        grace = 0
        self.connected = False

        while not self.connected:
            try:
                if self._connect():
                    self.connected = True
                elif grace < 5:
                    logger.info("No camera found. Waiting ...")
                    grace += 1
                    time.sleep(5)
                else:
                    logger.error("Could not connect to camera device.")
                    break
            except Exception as e:
                logger.error(f"Could not connect to camera device.\n{e}")
                return False

        return self.connected

    def run(self):
        self.capture_thread = threading.Thread(target=self.capture)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    def stop(self):
        self.connected = False
        self.capture_thread.join()  
        if self.capture_device is not None:
            self.capture_device.release()

    def capture(self):
        frame_id = 0
        while self.connected:
            if self.capture_device.isOpened():
                try:
                    status, frame_data = self.capture_device.read()
                    if status is not False:
                        self.buffer.put(Frame(data=frame_data[:, :], id=frame_id, timestamp=time.time()))
                        frame_id += 1
                except Exception as e:
                    logger.error(e)
            else:
                self.connected = False

    def _connect(self) -> bool:
        self.capture_device = cv2.VideoCapture(self.device_id)

        return self.capture_device.isOpened()
