from abc import ABCMeta, abstractmethod
from builtins import *


class Actuator(metaclass=ABCMeta):
    def __init__(self):
        super(Actuator, self).__init__()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass
