import traceback

from configparser import ConfigParser
from time import sleep
from threading import Thread

from core.base.buffer import SharedFrameBuffer, SharedFrameBufferReader
from core.ipc import IpcProcess
from core.utils import logger
from ipc.frame_writer_ipc import FrameWriterIpc

from tracking import MovementTracker

from ipc import MovementDetectionIpc

class MovementDetectionProcess(IpcProcess):
    def __init__(self, buffer: SharedFrameBuffer, config: ConfigParser) -> None:
        super().__init__(MovementDetectionIpc)

        self.config = config
        self.sfb_ref = buffer.get_reference("r")
        self.frame_writer: FrameWriterIpc = None

    def connect(self, target) -> MovementDetectionIpc:
        return super().connect(target)

    def run(self):
        self.sfb = SharedFrameBufferReader(self.sfb_ref)
        self.tracker = MovementTracker(self.sfb.shape)
        self.ipc_thread = Thread(target=self.ipc_loop, daemon=True)
        self.ipc_thread.start()

        while True:
            frame = self.sfb.get(blocking=True)
            try:
                if frame is not None:
                    if frame.id % self.config.getint("framerate") == 0:
                        movement = self.tracker.get_movement(frame.data)
                        if movement > self.config.getfloat('movement_threshold'):
                            self.frame_writer.reset()

            except Exception as e:
                logger.error(e)
                print(traceback.format_exc())

    def ipc_loop(self):
        while True:
            self.handle_ipc()
            sleep(1)
