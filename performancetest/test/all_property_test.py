# _*_ coding: utf-8 _*_
import time
from builtins import *

from performancetest.core.cpu import CpuMonitor
from performancetest.core.device import AndroidDevice
from performancetest.core.global_data import GlobalData as G
from performancetest.core.devicebattery import DeviceBatteryMonitor
from performancetest.core.fps import FPSMonitor
from performancetest.core.gpu import GpuMonitor
from performancetest.core.logcat import Logcat
from performancetest.core.memory import MemoryMonitor


def start():
    G.device = AndroidDevice(serialno="emulator-5554", server_addr=["localhost", "5037"],
                             package="com.road7.ddtdmxandroid.ld", save_dir="localhost")
    G.logcat = Logcat(package="com.road7.ddtdmxandroid.ld", save_dir="../core/")
    time.sleep(1)
    G.device.start_app()
    CpuMonitor("./cpu.txt").start()
    MemoryMonitor("./memory.txt").start()
    FPSMonitor("./FPS.txt").start()
    GpuMonitor("./gpu.txt").start()
    DeviceBatteryMonitor("./deviceBattery.txt").start()


def stop():
    G.stop_event.clear()


if __name__ == '__main__':
    start()
    time.sleep(30)
    stop()
