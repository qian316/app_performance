# _*_ coding: utf-8 _*_
import os
import signal
import time
from builtins import *
from multiprocessing import Process

from core.global_data import GlobalData as G
from core.base.actuator import Actuator
from core.cpu import CpuMonitor
from core.device import AndroidDevice
from core.devicebattery import DeviceBatteryMonitor
from core.fps import FPSMonitor
from core.gpu import GpuMonitor
from core.logcat import Logcat
from core.memory import MemoryMonitor


class TaskHandle(Process, Actuator):

    def __init__(self, serialno: str, server_addr: list[str], package: str, save_dir: str):
        super(TaskHandle, self).__init__()
        self.serialno = serialno
        self.server_addr = server_addr
        self.package = package
        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        self.daemon = True

    def start(self):
        super().start()

    def run(self):
        G.device = AndroidDevice(serialno=self.serialno, server_addr=self.server_addr,
                                 package=self.package, save_dir=self.save_dir)
        G.device.start_app()
        time.sleep(0.03)
        G.logcat = Logcat(package=self.package, save_dir=self.save_dir)
        CpuMonitor(os.path.join(self.save_dir, "cpu.csv")).start()
        MemoryMonitor(os.path.join(self.save_dir, "memory.csv")).start()
        FPSMonitor(os.path.join(self.save_dir, "fps.csv")).start()
        GpuMonitor(os.path.join(self.save_dir, "gpu.csv")).start()
        DeviceBatteryMonitor(os.path.join(self.save_dir, "devicebattery.csv")).start()
        # signal.signal(signal.SIGUSR1, self.stop())

    def stop(self):
        G.stop_event.clear()

    def suspend(self):
        G.suspend_event.clear()

    def handle_signal(self, signum, frame):
        print(f"{self.name} received {self.sig_name} signal")


if __name__ == '__main__':
    task_process = TaskHandle(serialno="E6E4C20629011168", server_addr=["10.130.131.80", "5039"],
                              package="com.happyelements.AndroidAnimal", save_dir="localhost")
    task_process.start()
    time.sleep(10)