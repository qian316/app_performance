# _*_ coding: utf-8 _*_
import os
import signal
import time
from builtins import *

import performancetest.core.global_data as G
from performancetest.core.base.actuator import Actuator
from performancetest.core.cpu import CpuMonitor
from performancetest.core.device import AndroidDevice
from performancetest.core.devicebattery import DeviceBatteryMonitor
from performancetest.core.fps import FPSMonitor
from performancetest.core.gpu import GpuMonitor
from performancetest.core.logcat import Logcat
from performancetest.core.memory import MemoryMonitor


class TaskHandle(Actuator):

    def __init__(self, serialno: str, server_addr: list[str], package: str, save_dir: str):
        super(TaskHandle, self).__init__()
        self.serialno = serialno
        self.server_addr = server_addr
        self.package = package
        self.save_dir = save_dir

    def start(self):
        super().start()

    def run(self):
        G.device = AndroidDevice(serialno=self.serialno, server_addr=self.server_addr,
                                 package=self.package, save_dir=self.save_dir)
        time.sleep(1)
        # G.logcat = Logcat(package=self.package, save_dir=self.save_dir)
        time.sleep(1)
        G.device.start_app()
        CpuMonitor(os.path.join(self.save_dir, "cpu.csv")).start()
        MemoryMonitor(os.path.join(self.save_dir, "memory.csv")).start()
        FPSMonitor(os.path.join(self.save_dir, "fps.csv")).start()
        GpuMonitor(os.path.join(self.save_dir, "gpu.csv")).start()
        DeviceBatteryMonitor(os.path.join(self.save_dir, "devicebattery.csv")).start()
        signal.signal(signal.SIGUSR1, self.stop())

    def stop(self):
        G.stop_event.clear()

    def suspend(self):
        G.suspend_event.clear()

    def handle_signal(self, signum, frame):
        print(f"{self.name} received {self.sig_name} signal")


if __name__ == '__main__':
    task_process = TaskHandle(serialno="emulator-5554", server_addr=["localhost", "5037"],
                              package="com.road7.ddtdmxandroid.ld", save_dir="localhost")
    task_process.run()
