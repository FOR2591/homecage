import os
import h5py
import sys
import time

import numpy as np

from collections import deque
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path
from threading import Thread
from typing import List

from core.base.buffer import SharedFrameBuffer, SharedFrameBufferReader
from core.base import Frame
from core.ipc import IpcProcess
from core.utils.log import logger
from ipc import FrameWriterIpc, ControllerIpc, FrameGrabberIpc, MovementDetectionIpc
from protocol import RecordingState
from utils import Interval

DTYPES = {'BGR3': np.uint8, 'RGB3': np.uint8, 'Y16 ': np.uint16, 'Y16': np.uint16}

class FrameWriterProcess(IpcProcess):
    def __init__(self, idx: int, buffer: SharedFrameBuffer, config: ConfigParser) -> None:
        super().__init__(FrameWriterIpc)

        self.sfb_ref = buffer.get_reference("r")
        self.config = config

        self.controller: ControllerIpc = None
        self.grabber: FrameGrabberIpc = None
        self.idx = idx
        self.state = RecordingState.STATE_IDLE

        self.last_frame_ts: float = 0
        self.watchdog: int = 0

    def connect(self, target) -> FrameWriterIpc:
        return super().connect(target)
        
    def run(self):
        self.sfb = SharedFrameBufferReader(self.sfb_ref)

        self._init_write_buffer()
        self._start_watchdog()

        while True:
            try:
                self.handle_ipc()
                
                frame = self.sfb.get()
                if self.state == RecordingState.STATE_RECORDING:
                    if frame is not None and np.sum(frame.data[:10, :10]) > 0:
                        self.last_frame_ts = frame.timestamp
                        self._write_to_buffer(frame)

                if self.state == RecordingState.STATE_WAITING:
                    pass

                if self.state == RecordingState.STATE_ERROR and frame is None:
                    time.sleep(1)

                elif self.state == RecordingState.STATE_IDLE and frame is None:
                    time.sleep(1)

            except Exception as e:
                logger.error(e)
                self._set_state(RecordingState.STATE_ERROR)

    def reset(self):
        if self.state == RecordingState.STATE_RECORDING:
            self._init_write_buffer()

    def start_recording(self):
        if self.state == RecordingState.STATE_RECORDING:
            logger.warn("Cannot start recording (recording is still running)")

        if self.state == RecordingState.STATE_WAITING:
            logger.warn("Cannot start recording (recording is still writing data)")
            self.grabber.stop_frame_acquisition()

        if self.state == RecordingState.STATE_IDLE:
            self.last_frame_ts = time.time()
            self._set_state(RecordingState.STATE_RECORDING)
            self._init_write_buffer()
            logger.info("Starting to record data")

    def stop_recording(self):
        if self.state == RecordingState.STATE_RECORDING:
            self._set_state(RecordingState.STATE_IDLE)
        elif self.state == RecordingState.STATE_ERROR:
            self._set_state(RecordingState.STATE_IDLE)
            logger.warn("Recovering from error state")
        else:
            logger.warn("Frame writer is currently not recording")

    def _set_state(self, state: RecordingState):
        self.state = state
        self.controller.update_writer_state(self.idx, state)

    def _init_write_buffer(self):
        w, h, c = int(self.config['width']), int(self.config['height']), int(self.config['channels'])
        nb_frames = int(int(self.config['framerate']) * int(self.config['recording_duration_sec']))
        dtype = DTYPES[self.config['encoding']]

        self.write_buffer = np.zeros((nb_frames, h, w, c), dtype=dtype)
        self.ts_buffer = np.zeros((nb_frames), dtype = float)
        self.write_idx = 0

    def _write_to_buffer(self, frame: Frame):
        self.write_buffer[self.write_idx, :] = frame.data
        self.ts_buffer[self.write_idx] = frame.timestamp
        self.write_idx += 1

        if self.write_idx == self.write_buffer.shape[0]:
            self._set_state(RecordingState.STATE_WAITING)
            self.grabber.stop_frame_acquisition()

            t = Thread(target=self._write_to_file)
            t.start()

    def _write_to_file(self):
        try:
            path = self.config['export_path']
            Path(path).mkdir(parents=True, exist_ok=True)

            ctype = self.config['type']
            fname = f"{datetime.now().strftime('%Y_%m_%dT_%H_%M_%S')}_{ctype}.h5"

            logger.info('Writing data to disk')

            with h5py.File(os.path.join(path, fname), 'a', libver='latest') as file:
                group = file.require_group("data_raw")
                group.create_dataset(f'data', data=self.write_buffer, dtype=self.write_buffer.dtype)
                group.create_dataset(f'timestemps', data=self.ts_buffer, dtype=self.ts_buffer.dtype)

            self._set_state(RecordingState.STATE_IDLE)
            logger.info('Finished writing')

        except Exception as e:
            logger.error(e)
            self.grabber.stop_frame_acquisition()
            self._set_state(RecordingState.STATE_ERROR)

    def _start_watchdog(self):
        self.watchdog = Interval.set_interval(self._watchdog, 1)

    def _watchdog(self):
        if self.state == RecordingState.STATE_RECORDING:
            if (time.time() - self.last_frame_ts) > 10:
                logger.error(f"Watchdog triggered for {self.config['type']}")
                self.last_frame_ts = time.time()
                self.grabber.reset()
