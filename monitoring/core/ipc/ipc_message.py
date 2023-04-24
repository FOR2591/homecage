import uuid

class IpcMessage():

    def __init__(self, cmd, origin, *args, **kwargs):
        self.id = str(uuid.uuid4())
        self.cmd = str(cmd)
        self.origin = origin
        self.args = args
        self.kwargs = kwargs