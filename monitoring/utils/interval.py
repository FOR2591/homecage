import time

from concurrent.futures import thread

from threading import Thread

from typing import Dict, Callable

class Interval(Thread):
    __active_intervals = {}

    def __init__(self, func: Callable, interval: int, *args, **kwargs) -> None:
        super().__init__()

        self.args = args
        self.kwargs = kwargs

        self.interval = interval
        self.func = func
        self.running = False

    def run(self) -> None:
        self.running = True
        self.execution_time = time.time()

        while self.running:
            if time.time() >= self.execution_time:
                self.execution_time += self.interval
                self.func(*self.args, **self.kwargs)
            else:
                time.sleep(1)

    @staticmethod
    def get_interval(ident: int):
        return Interval.__active_intervals[ident]

    @staticmethod
    def set_interval(func: Callable, interval: int, *args, **kwargs) -> int:
        t = Interval(func, interval,  *args, **kwargs)
        t.start()

        Interval.__active_intervals[t.ident] = t

        return t.ident

    @staticmethod
    def clear_interval(ident: int):
        try:
            t : Interval = Interval.__active_intervals[ident]
            t.running = False

            del Interval.__active_intervals[ident]
        except:
            pass