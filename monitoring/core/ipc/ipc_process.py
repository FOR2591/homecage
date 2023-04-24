import uuid

from multiprocessing import Process, Queue
from threading import Thread
from typing import Dict

from core.ipc import IpcInterface, IpcMessage

class IpcProcess(Process):
    def __init__(self, ipc: IpcInterface):
        super().__init__()
        self.address = str(uuid.uuid4())
        self.return_stack = {}
        self.input_queue = Queue()
        self.output_queues: Dict[Queue] = {}
        
        self.ipc = ipc
        self.main_process = None
        self.exit = False

    def connect(self, target) -> IpcInterface:
        target.output_queues[self.address] = self.input_queue
        self.output_queues[target.address] = target.input_queue
        
        return self.ipc(self.input_queue, target.address, target.return_stack)

    def handle_ipc(self):
        if self.input_queue.qsize() >= 1:
            msg: IpcMessage = self.input_queue.get()
            if msg.cmd != "return":
                ret = getattr(self, msg.cmd)(*msg.args, **msg.kwargs)
                self.send_return(ret, msg)
            else:
                if(msg.id in self.return_stack):
                    self.return_stack[msg.id](*msg.args, **msg.kwargs)

    def send_return(self, ret, msg):
        ret_msg = IpcMessage("return", None, ret)
        ret_msg.id = msg.id
        self.output_queues[msg.origin].put(ret_msg)

    def quit(self) -> None:
        self.exit = True
        self.terminate()
