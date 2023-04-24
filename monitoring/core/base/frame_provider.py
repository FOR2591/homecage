from abc import abstractmethod

class FrameProvider():
    """
    Abstract base class for a video source, providing the base interface and common functionality
    """

    def __init__(self):
        """
        Class constructor
        """
        super().__init__()
        self.connected = False
        self.completed = False

    @abstractmethod
    def connect(self):
        """
        Connect to the video source. Pure virtual method. Needs to be overwritten by child class
        """
        return

