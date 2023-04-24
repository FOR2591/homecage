from core.ipc import IpcInterface, IpcMethod
from protocol import RecordingState
class FrameGrabberIpc(IpcInterface):

    ### Hacky ###
    state: RecordingState = RecordingState.STATE_IDLE

    @IpcMethod
    def start_frame_acquisition(self) -> None:
        pass

    @IpcMethod    
    def stop_frame_acquisition(self) -> None:
        pass

    @IpcMethod    
    def reset(self) -> None:
        pass