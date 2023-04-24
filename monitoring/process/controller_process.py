import os
import shutil
import sys
import time

from numpy import number 
from pathlib import Path
from typing import List, Dict

from core.ipc import IpcProcess
from core.utils import logger
from ipc import ControllerIpc
from ipc.frame_grabber_ipc import FrameGrabberIpc
from ipc.frame_writer_ipc import FrameWriterIpc
from protocol import DeviceInfo, HomecageCommand, Commands, CameraDevice, RecordingMode, RecordingState, RecordingStatus, ResDeviceInfo, DeviceType, Storage
from utils.interval import Interval
from websocket import WsClient

class ControllerProcess(IpcProcess):
    
    def __init__(self, host_config, camera_configs):
        super().__init__(ControllerIpc)

        self.host_config = host_config
        self.camera_configs = camera_configs

        self.device_info = self._init_device_info()

        self.frame_grabber: List[FrameGrabberIpc] = []
        self.frame_writer: List[FrameWriterIpc] = []
        self.interval_timers: List[int] = []

        self.state = RecordingState.STATE_IDLE

    def connect(self, target) -> ControllerIpc:
        return super().connect(target)

    def run(self):
        # if sys.platform != 'win32':
        #     os.system("taskset -p 0x01 %d" % os.getpid())

        self.connect_ws()
        while True:
            self.handle_ipc()

            if self.state == RecordingState.STATE_IDLE:
                time.sleep(1)

    def connect_ws(self):
        self.ws = WsClient(f'ws://{self.host_config["webserver_hostname"]}:{self.host_config["webserver_port"]}', on_open=self._on_open, on_message=self._on_message) 
        self.ws.start()

    def get_state(self):
        pass

    def send_device_info(self):
        cmd = HomecageCommand()
        cmd.client_name = self.host_config["client_name"]
        cmd.command = Commands.CMD_RES_DEVICE_INFO
        cmd.res_device_info = ResDeviceInfo()

        self.device_info.storage = Storage(total=self._disk_usage().total, free=self._disk_usage().free)

        cmd.res_device_info.device_infos.append(self.device_info)
        self.send_command(cmd)

    def send_command(self, cmd: HomecageCommand):
        print(cmd.to_json())
        self.ws.emit("msg", cmd.to_json())

    def start_interval_recording(self, idx : number):
        interval_seconds = int(self.camera_configs[idx]["recording_interval_sec"])
        recording_interval = Interval.set_interval(self._record, interval_seconds, idx)
        self.interval_timers.append({"interval_id": recording_interval, "idx":idx, "interval": interval_seconds, "start": time.time()})
        
    def start_recording(self):
        self.state = RecordingState.STATE_RECORDING
        for idx in range(len(self.frame_writer)):
            self.start_interval_recording(idx)

    def stop_recording(self):
        for idx, interval in enumerate(self.interval_timers):
            Interval.clear_interval(interval["interval_id"])

            self.frame_grabber[idx].stop_frame_acquisition()
            self.frame_writer[idx].stop_recording()

        self.interval_timers = []
        self.state = RecordingState.STATE_IDLE

    def update_grabber_state(self, idx: int, state: RecordingState) -> None:
        self.frame_grabber[idx].state  = state
        self.update_device_state()

    def update_writer_state(self, idx: int, state: RecordingState) -> None:
        self.frame_writer[idx].state  = state
        self.update_device_state()

    def update_device_state(self) -> None:
        for idx, (grabber, writer) in enumerate(zip(self.frame_grabber, self.frame_writer)):
            print(writer.state, self.state)
            if grabber.state == RecordingState.STATE_ERROR or writer.state == RecordingState.STATE_ERROR:
                self.device_info.cameras[idx].state = RecordingState.STATE_ERROR
                self.device_info.cameras[idx].status = RecordingStatus.STATUS_ERROR
        
            elif grabber.state == RecordingState.STATE_RECORDING and writer.state == RecordingState.STATE_RECORDING:
                self.device_info.cameras[idx].state = RecordingState.STATE_RECORDING
                self.device_info.cameras[idx].status = RecordingStatus.STATUS_RECORDING

            elif grabber.state == RecordingState.STATE_RECORDING and writer.state == RecordingState.STATE_WAITING:
                self.device_info.cameras[idx].state = RecordingState.STATE_RECORDING
                self.device_info.cameras[idx].status = RecordingStatus.STATUS_WAITING

            elif grabber.state == RecordingState.STATE_IDLE and writer.state == RecordingState.STATE_WAITING:
                self.device_info.cameras[idx].state = RecordingState.STATE_IDLE
                self.device_info.cameras[idx].status = RecordingStatus.STATUS_WAITING

            elif self.state == RecordingState.STATE_RECORDING and writer.state == RecordingState.STATE_IDLE:
                self.device_info.cameras[idx].state = RecordingState.STATE_RECORDING
                self.device_info.cameras[idx].status = RecordingStatus.STATUS_READY

                for interval in self.interval_timers:
                    if interval["idx"] == idx:
                        self.device_info.cameras[idx].shedule = int(Interval.get_interval(interval["interval_id"]).execution_time)
            else:
                self.device_info.cameras[idx].state = RecordingState.STATE_IDLE
                self.device_info.cameras[idx].status = RecordingStatus.STATUS_READY
        
        self.send_device_info()

    def _init_device_info(self) -> DeviceInfo:
        device_info = DeviceInfo()
        device_info.device_name = self.host_config["client_name"]
        device_info.device_type = DeviceType.TYPE_RPI
        device_info.storage = Storage(total=self._disk_usage().total, free=self._disk_usage().free)
        
        for idx, camera_config in enumerate(self.camera_configs):
            cd = CameraDevice(id=idx, width=camera_config["width"], height=camera_config["height"], channels=camera_config["channels"], fps=camera_config["framerate"], enconding=camera_config["encoding"], type=camera_config["type"], state=RecordingState.STATE_IDLE, mode=RecordingMode.MODE_INTERVAL, status=RecordingStatus.STATUS_READY, shedule=0)
            device_info.cameras.append(cd)

        return device_info

    def _disk_usage(self):
        try:
            path = self.camera_configs[0]["export_path"]
            Path(path).mkdir(parents=True, exist_ok=True)

            return shutil.disk_usage(self.camera_configs[0]["export_path"])
        except Exception as e:
            logger.error(e)
            return shutil.disk_usage('./')

    def _on_message(self, msg: str) -> None:
        msg : HomecageCommand = HomecageCommand().from_json(msg)

        if msg.command == Commands.CMD_REQ_SET_RECORDING_STATE:
            if self.state == RecordingState.STATE_IDLE and msg.req_set_recording_state.state == RecordingState.STATE_RECORDING:
                self.start_recording()
            elif self.state == RecordingState.STATE_RECORDING and msg.req_set_recording_state.state == RecordingState.STATE_IDLE:
                self.stop_recording()

    def _on_open(self) -> None:
        logger.info("Connect")
        self.send_device_info()

    def _record(self, idx: int):
        grabber = self.frame_grabber[idx]
        writer = self.frame_writer[idx]

        writer.start_recording()
        grabber.start_frame_acquisition()

    def _query_devices(self) ->None:
        pass


