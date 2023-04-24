from multiprocessing import Queue

from .ipc_message import IpcMessage

def IpcMethod(func):
    def wrapper(*args, callback=None, **kwargs):
        msg = IpcMessage(func.__name__, args[0].address, *args[1:], **kwargs)
        
        if callback:
            args[0].return_stack[msg.id] = callback

        args[0].queue.put(msg)

    return wrapper

class IpcInterface:
    def __init__(self, queue: Queue, address: str, return_stack):
        self.queue = queue
        self.address = address
        self.return_stack = return_stack