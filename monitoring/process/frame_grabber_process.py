import cv2
import os
import sys

from configparser import ConfigParser

from core.base.buffer import SharedFrameBuffer, SharedFrameBufferWriter
from core.frame_provider import OCVProvider
from core.ipc import IpcProcess
from core.utils import logger
from utils import ErrorHandler

from time import sleep, time 
from ipc import FrameGrabberIpc, ControllerIpc
from protocol import RecordingState

class CameraFrameProvider(OCVProvider):
    def __init__(self, buffer: SharedFrameBuffer, config: ConfigParser, device_id=0):
        super().__init__(buffer, device_id=device_id)

        self.config = config
        self.encoding = cv2.VideoWriter.fourcc(*f"{self.config['encoding']:4s}")


    def _connect(self) -> bool:
        if sys.platform == 'win32':
            self.capture_device = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
        else:
            self.capture_device = cv2.VideoCapture(self.device_id, cv2.CAP_V4L2)
        self.capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.config["width"]))
        self.capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.config["height"]))
        self.capture_device.set(cv2.CAP_PROP_FPS, int(self.config['framerate']))

        if self.encoding == cv2.VideoWriter.fourcc('Y','1','6',' '):
            self.capture_device.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)

        self.capture_device.set(cv2.CAP_PROP_FOURCC, self.encoding)

        return self.capture_device.isOpened()

class FrameGrabberProcess(IpcProcess):

    def __init__(self, idx: int, buffer: SharedFrameBuffer, config: ConfigParser) -> None:
        super().__init__(FrameGrabberIpc)

        self.sfb_ref = buffer.get_reference(mode="w")
        self.config = config

        self.idx = idx
        self.state = RecordingState.STATE_IDLE
        self.controller: ControllerIpc = None
    
    def connect(self, target) -> FrameGrabberIpc:
        return super().connect(target)

    def run(self) -> None:
        # if sys.platform != 'win32':
        #     os.system("taskset -p 0x02 %d" % os.getpid())
    
        self.sfb = SharedFrameBufferWriter(self.sfb_ref)
        self.fp = CameraFrameProvider(self.sfb, self.config, device_id=int(self.config["device_id"]))

        while True:
            try:
                self.handle_ipc()
                if self.state == RecordingState.STATE_RECORDING:
                    if not self.fp.connected:
                        logger.error("Error while writing frames to buffer")
                        self._set_state(RecordingState.STATE_ERROR)
                        
                sleep(1)
            except Exception as e:
                self._set_state(RecordingState.STATE_ERROR)
                logger.error(e)

                self.stop_frame_acquisition()

    def start_frame_acquisition(self) -> None:
        try:
            if self.state == RecordingState.STATE_IDLE:
                if self.fp.connect():
                    self._set_state(RecordingState.STATE_RECORDING)
                    logger.info("Started frame acquisition")
                    self.fp.run()
                else:
                    self._set_state(RecordingState.STATE_ERROR)
                    logger.error("Could not start frame acquisiton")
            if self.state == RecordingState.STATE_ERROR:
                if self.fp.connect():
                    logger.info("Started frame acquisition from error state")
                    self.fp.run()
                else:
                    logger.error("Could not start frame acquisiton")
        except Exception as e:
            self._set_state(RecordingState.STATE_ERROR)
            logger.error(f"Could not start frame acquisiton: {e}")

    def stop_frame_acquisition(self):
        try:
            self.fp.stop()
            if self.state == RecordingState.STATE_RECORDING:
                logger.info("Finished frame acquisition")
            if self.state == RecordingState.STATE_ERROR:
                logger.info("Recovering from error state")

            self._set_state(RecordingState.STATE_IDLE)
        except:
            try:
                self.fp = CameraFrameProvider(self.sfb, self.config, device_id=int(self.config["device_id"]))
                self._set_state(RecordingState.STATE_ERROR)
            except:
                logger.info("Cannot recover from error state")

    def reset(self):
        logger.info(f"Resetting {self.config['type']}")
        try:
            self.stop_frame_acquisition()
        except Exception as e:
            logger.error(f"Could not stop capture thread: {e}")

        try:
            if self.config['type'] == "Lepton":
                if ErrorHandler.reset_lepton():
                    logger.info("Lepton reset successfully")
                else:
                    logger.info("Lepton reset failed (is the camera still connected?)")

        except Exception as e:
            logger.info(f"Cannot reset {self.config['type']} frame provider: {e}")

    def _set_state(self, state: RecordingState):
        self.state = state
        self.controller.update_grabber_state(self.idx, state)
