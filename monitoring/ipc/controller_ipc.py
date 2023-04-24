from core.ipc import IpcInterface, IpcMethod
from protocol import RecordingState

class ControllerIpc(IpcInterface):
    
    @IpcMethod
    def update_grabber_state(self, idx: int,  state: RecordingState) -> None:
        pass

    @IpcMethod
    def update_writer_state(self, idx: int,  state: RecordingState) -> None:
        pass