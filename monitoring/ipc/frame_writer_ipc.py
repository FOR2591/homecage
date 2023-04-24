from core.ipc import IpcInterface, IpcMethod
from protocol import RecordingState
class FrameWriterIpc(IpcInterface):

    ### Hacky ###
    state: RecordingState = RecordingState.STATE_IDLE
    
    @IpcMethod
    def start_recording(self) -> None:
        pass

    @IpcMethod
    def stop_recording(self)  -> None:
        pass

    @IpcMethod
    def reset(self) -> None:
        pass
