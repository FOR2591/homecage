import os
import sys
import time

import numpy as np

from configparser import ConfigParser
from typing import List

from core.ipc import IpcProcess
from core.base.buffer import SharedFrameBuffer
from core.utils import logger
from ipc import MainIpc
from process import ControllerProcess, FrameGrabberProcess, FrameWriterProcess, MovementDetectionProcess

STATE_IDLE = 'IDLE'

DTYPES = {'BGR3': np.uint8, 'RGB3': np.uint8, 'Y16 ': np.uint16, 'Y16': np.uint16}
class MainProcess(IpcProcess):
    def __init__(self, host_config: ConfigParser, camera_configs: List[ConfigParser]):
        super().__init__(MainIpc)

        self.host_config = host_config
        self.camera_configs = camera_configs

        self.frame_buffer: List[SharedFrameBuffer] = []
        self.frame_grabber: List[FrameGrabberProcess] = []
        self.frame_writer: List[FrameWriterProcess] = []
        self.movement_detector: List[MovementDetectionProcess] = []

    def connect(self, target) -> MainIpc:
        return super().connect(target)

    def run(self):
        # if sys.platform != 'win32':
        #     os.system("taskset -p 0x01 %d" % os.getpid())

        self._create_buffers()
        self._create_processes()
        self._start_processes()
        time.sleep(10)

        while True: 
            self.handle_ipc()
            # if self.state == STATE_IDLE:
            time.sleep(1)
    
    def _create_buffers(self) -> None:
        for camera_config in self.camera_configs:
            dtype = DTYPES[camera_config['encoding']]
            size = int(camera_config['buffer_size'])
            w, h, c = int(camera_config['width']), int(camera_config['height']), int(camera_config['channels'])

            self.frame_buffer.append(SharedFrameBuffer((h, w, c), size=size, dtype=dtype))

    def _create_processes(self) -> None: 
        self.controller = ControllerProcess(self.host_config, self.camera_configs)
        
        for idx, camera_config in enumerate(self.camera_configs):
            frame_grabber = FrameGrabberProcess(idx, buffer=self.frame_buffer[idx], config=camera_config)
            frame_writer = FrameWriterProcess(idx, buffer=self.frame_buffer[idx], config=camera_config)

            frame_grabber.controller = self.controller.connect(frame_grabber)
            frame_writer.controller = self.controller.connect(frame_writer)
            frame_writer.grabber = frame_grabber.connect(frame_writer)
            
            if camera_config.getboolean('recording_movement') is False:
                movement_detection = MovementDetectionProcess(self.frame_buffer[idx], config=camera_config)
                movement_detection.frame_writer = frame_writer.connect(movement_detection)
                self.movement_detector.append(movement_detection)

            self.controller.frame_grabber.append(frame_grabber.connect(self.controller))
            self.controller.frame_writer.append(frame_writer.connect(self.controller))
            self.frame_grabber.append(frame_grabber)
            self.frame_writer.append(frame_writer)

    def _start_processes(self) -> None:
        self.controller.start()

        for frame_writer, frame_grabber in zip(self.frame_writer, self.frame_grabber):
            frame_writer.start()
            frame_grabber.start()

        for movement_detector in self.movement_detector:
            movement_detector.start()

