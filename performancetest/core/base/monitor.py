from abc import ABCMeta, abstractmethod
from builtins import *
from threading import Thread


class Monitor(Thread, metaclass=ABCMeta):
    def __init__(self):
        super(Monitor, self).__init__()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass
