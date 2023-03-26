import csv
import re
import threading
import time
import traceback
from builtins import *

from global_data import GlobalData as G, logger
from performancetest.core.base.monitor import Monitor


class ParsMeminfo(object):
    RE_TOTAL_PSS = re.compile(r'TOTAL\s+(\d+)')

    def __init__(self, meminfo):
        self.meminfo = meminfo
        self.taltol_pss = self.get_taltol_pss()

    def get_taltol_pss(self):
        match = self.RE_TOTAL_PSS.search(self.meminfo)
        if match:
            return round(float(match.group(1)) / 1024, 2)
        else:
            return ""


class MemoryMonitor(Monitor):
    def __init__(self, save_file, interval=1, test_time=-1):
        super().__init__()
        self.save_file = save_file
        self.test_time = test_time
        self.interval = interval

    def get_mem_info(self):
        if G.device.sdkversion > 25:
            mem_info = G.device.adb.raw_shell("top -n 1 -p {} -o RES -b -q".format(G.device.package_pid)).decode()
            mem_info = mem_info.strip()
            return mem_info
        else:
            mem_info = G.device.adb.raw_shell("dumpsys meminfo {}".format(G.device.package)).decode()
            mem_info = str(ParsMeminfo(mem_info).taltol_pss)
        logger.info("当前获取到的mem信息是{}".format(mem_info))
        return mem_info

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
        按照指定频率，循环搜集内存的信息
        '''
        mem_title = ["timestamp", "memory"]
        mem_file = self.save_file
        with open(mem_file, 'w+') as df:
            csv.writer(df, lineterminator='\n').writerow(mem_title)
        G.stop_event.set()  # 启动
        G.suspend_event.set()  # 启动
        while G.stop_event.is_set():  # 停止了循环会停止
            G.suspend_event.wait()  # 暂停时会暂停在这里
            mem_list = []
            try:
                logger.debug("---------------开始获取手机内存信息, into _collect_package_mem_thread loop thread is : " + str(
                    threading.current_thread().name))
                before = time.time()
                mem_list.append(before)
                # 为了mem值的准确性，将采集的时间间隔放在top命令中了
                mem_info = self.get_mem_info()
                if "G" in mem_info:
                    mem_info = float(mem_info.replace("G", "")) * 1024
                elif "M" in mem_info:
                    mem_info = float(mem_info.replace("M", ""))
                mem_list.append(mem_info)
                after = time.time()
                time_consume = after - before
                logger.debug("  ============== time consume for mem info : " + str(time_consume))
                if mem_list == None or mem_list == '':
                    logger.debug("can't get memory info")
                    logger.info("重新获取pid,重启logcat")
                    if G.run_mode != "airtest_monkey":
                        logger.info("重新获取pid,重启logcat")
                        G.logcat.restart()
                    G.device.get_pid()
                logger.info(mem_file + "*****************************")
                if not mem_info:
                    mem_list[-1] = 0
                with open(mem_file, 'a+', encoding="utf-8") as df:
                    csv.writer(df, lineterminator='\n').writerow(mem_list)
                    del mem_list[:]
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as e:
                logger.error("an exception hanpend in memory thread , reason unkown!, e:")
                logger.error(traceback.format_exc())
                G.device.get_pid()
        logger.debug("memory stop event is set or timeout")


if __name__ == "__main__":
    from device import AndroidDevice

    G.device = AndroidDevice(serialno="emulator-5554", server_addr=["localhost", "5037"],
                             package="com.road7.ddtdmxandroid.ld", save_dir="localhost")
    G.device.start_app()
    mem = MemoryMonitor("./memory.txt")
    mem.start()
    time.sleep(10)
    mem.stop()
