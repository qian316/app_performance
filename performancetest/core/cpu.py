# coding=utf-8
import sys

sys.path.append("../")
import csv
import os
import threading
import time
import traceback
from builtins import *

from performancetest.core.base.monitor import Monitor
from performancetest.core.global_data import GlobalData as G, logger


class ParseCpuinfo(object):
    def __init__(self, package, cpuinfo, sdkversion=None):
        self.cpuinfo = cpuinfo
        self.package = package
        self.sdkversion = sdkversion
        self.cpur_rate = self.get_cpu_rate()

    def get_cpu_rate(self):
        # logger.info("top获取到的原始信息是{}".format(self.cpuinfo))
        for pidinfo in self.cpuinfo.split(os.linesep):
            if self.package in pidinfo:
                pidinfo = pidinfo.split()
                if pidinfo[-1] == self.package:
                    return pidinfo[4].replace("%", '')
        return ''


class CpuMonitor(Monitor):
    def __init__(self, save_file, test_time=-1, interval=1):
        super().__init__()
        self.save_file = save_file
        self.test_time = test_time
        self.interval = interval

    def get_cpuinfo(self):
        if G.device.sdkversion >= 25:
            cpu_info = G.device.adb.raw_shell("top -n 1 -p {} -o %CPU -b -q".format(G.device.package_pid)).decode()
            cpu_info = cpu_info.strip()
        else:
            cpu_info = G.device.adb.raw_shell("top -n 1".format(G.device.package_pid)).decode()
            cpu_info = ParseCpuinfo(G.device.package, cpu_info, G.device.sdkversion).cpur_rate
        logger.info("获取到的cpu信息是：{}".format(cpu_info))
        return cpu_info

    def start(self):
        super(Monitor, self).start()

    # 结束任务
    def stop(self):
        G.stop_event.clear()

    # 暂停任务
    def suspend(self):
        G.suspend_event.clear()

    def run(self):
        '''
        按照指定频率，循环搜集cpu的信息
        :return:
        '''
        cpu_title = ["timestamp", "cpu%"]
        cpu_file = self.save_file
        with open(cpu_file, 'w+') as df:
            csv.writer(df, lineterminator='\n').writerow(cpu_title)
        G.stop_event.set()  # 启动
        G.suspend_event.set()  # 启动
        while G.stop_event.is_set():  # 停止了循环会停止
            G.suspend_event.wait()  # 暂停时会暂停在这里
            cpu_list = []
            try:
                logger.debug("---------------开始获取cpu信息, into _collect_package_cpu_thread loop thread is : " + str(
                    threading.current_thread().name))
                before = time.time()
                cpu_list.append(before)
                # 为了cpu值的准确性，将采集的时间间隔放在top命令中了
                cpu_info = self.get_cpuinfo()
                cpu_list.append(cpu_info)
                after = time.time()
                time_consume = after - before
                logger.debug(
                    "============== time consume for cpu info : {0}, value {1}".format(time_consume, cpu_info))
                if cpu_info == None or cpu_info == '' or float(cpu_info) == 0:
                    logger.error("can't get cpu info")
                    G.device.get_pid()
                    logger.info("重新获取pid,重启logcat")
                    G.logcat.restart()
                    # 取消获取不到跳过，默认给0
                    cpu_list[-1] = 0
                with open(cpu_file, 'a+', encoding="utf-8") as df:
                    csv.writer(df, lineterminator='\n').writerow(cpu_list)
                    del cpu_list[:]
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as e:
                logger.error("an exception hanpend in cpu thread , reason unkown!, e:")
                traceback.print_exc()
                G.device.get_pid()
        logger.debug("cpu stop event is set or timeout")


if __name__ == "__main__":
    from device import AndroidDevice

    G.device = AndroidDevice(serialno="emulator-5554", server_addr=["localhost", "5037"],
                             package="com.road7.ddtdmxandroid.ld", save_dir="localhost")
    G.device.start_app()
    cpu = CpuMonitor("./cpu.txt")
    cpu.start()
    time.sleep(15)
    cpu.stop()
