# coding=utf-8
import csv
import os
import threading
import time
import traceback
from builtins import *

from .global_data import GlobalData as G, logger
from .base.monitor import Monitor


class DeviceBatteryFomatter(object):

    def __init__(self, device_battery):
        self.device_battery = device_battery
        self.property_info = self.device_battery.split(os.linesep)
        self.temperature = self.get_temperature()
        self.level = self.get_level()
        self.charge = self.get_charge()

    def get_temperature(self):
        return float(self.get_target_proerty("temperature")) * 0.1

    def get_level(self):
        return self.get_target_proerty("level")

    def get_charge(self):
        return str(self.get_target_proerty("status")) == "2" or self.get_target_proerty("USB powered") == "true"

    def get_target_proerty(self, target):
        try:
            for p in self.property_info:
                if target in p:
                    return p.strip().split(": ")[1]
            return None
        except Exception as e:
            logger.error(e)
            return None

    def __repr__(self):
        return str({"property": self.property_info})


class DeviceBatteryMonitor(Monitor):
    def __init__(self, save_file, test_time=-1, interval=1):
        super().__init__()
        self.save_file = save_file
        self.test_time = test_time
        self._stop_event = threading.Event()
        self.interval = interval

    def get_device_battery_info(self):
        device_battery_info = G.device.adb.raw_shell("dumpsys battery".format(G.device.serialno)).decode()
        device_battery_info = DeviceBatteryFomatter(device_battery_info)
        logger.info("获取到的设备信息是：{}".format(device_battery_info))
        return device_battery_info

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
        按照指定频率，循环搜集设备温度的信息
        :return:
        '''
        device_battery_title = ["timestamp", "devicetemperature", "devicebatterylevel%", "charge"]
        device_battery_file = self.save_file
        with open(device_battery_file, 'w+') as df:
            csv.writer(df, lineterminator='\n').writerow(device_battery_title)
        G.stop_event.set()  # 启动
        G.suspend_event.set()  # 启动
        while G.stop_event.is_set():  # 停止了循环会停止
            G.suspend_event.wait()  # 暂停时会暂停在这里
            device_battery_info_list = []
            try:
                logger.debug("---------------开始获取手机温度 电量信息: " + str(
                    threading.current_thread().name))
                before = time.time()
                device_battery_info = self.get_device_battery_info()
                device_battery_info_list.append(before)
                device_battery_info_list.append(device_battery_info.temperature)
                device_battery_info_list.append(device_battery_info.level)
                device_battery_info_list.append(device_battery_info.charge)
                after = time.time()
                time_consume = after - before
                logger.debug("  ============== time consume for devicetemperature info : " + str(time_consume))
                logger.info(device_battery_file + "*****************************")
                with open(device_battery_file, 'a+', encoding="utf-8") as df:
                    csv.writer(df, lineterminator='\n').writerow(device_battery_info_list)
                    del device_battery_info_list[:]
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as e:
                logger.error("an exception hanpend in devicebatteryinfo thread , reason unkown!, e:")
                traceback.print_exc()
                G.device.get_pid()
        logger.debug("memory stop event is set or timeout")


if __name__ == "__main__":
    from device import AndroidDevice

    G.device = AndroidDevice(serialno="emulator-5554", server_addr=["localhost", "5037"],
                             package="com.road7.ddtdmxandroid.ld", save_dir="localhost")
    G.device.start_app()
    d = DeviceBatteryMonitor("./deviceBattery.txt")
    d.start()
    time.sleep(5)
    d.stop()
