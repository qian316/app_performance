# _*_ coding: utf-8 _*_
import sys

sys.path.append("../")
import os
import time
from builtins import *
from multiprocessing import Process

from sqlalchemy import desc

from performancetest.core.base.actuator import Actuator
from performancetest.core.cpu import CpuMonitor
from performancetest.core.device import AndroidDevice
from performancetest.core.devicebattery import DeviceBatteryMonitor
from performancetest.core.fps import FPSMonitor
from performancetest.core.global_data import GlobalData as G
from performancetest.core.gpu import GpuMonitor
from performancetest.core.logcat import Logcat
from performancetest.core.memory import MemoryMonitor
from performancetest.core.snapshot import SnapshotMonitor
from performancetest.web.dao import connect, Task


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
        # signal.signal(signal.SIGTERM, self.stop())
        # signal.signal(signal.SIGINT, self.stop())

    def start(self):
        super().start()

    def run(self):
        with connect() as session:
            current_task_running = session.query(Task).filter(Task.host == self.server_addr[0]).filter(
                Task.port == self.server_addr[1]).filter(Task.status == 0).order_by(desc(Task.start_time)).first()
            current_task_running.status = 1
            current_task_running.pid = self.pid
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
        SnapshotMonitor(os.path.join(self.save_dir, "picture_log"), self.serialno, self.server_addr).start()

    def stop(self):
        G.stop_event.clear()

    def suspend(self):
        G.suspend_event.clear()


if __name__ == '__main__':
    task_process = TaskHandle(serialno="E6E4C20629011168", server_addr=["10.130.131.80", "5039"],
                              package="com.happyelements.AndroidAnimal", save_dir="localhost")
    task_process.start()
    time.sleep(10)
