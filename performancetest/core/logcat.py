# coding=utf8
import os
import subprocess
import threading
import time
from builtins import *

from global_data import GlobalData as G, logger
from performancetest.core.base.monitor import Monitor

LOGCAT_FILE_NAE = "logcat.txt"


class Logcat(Monitor):
    '''
    logcat收集器
    '''

    def __init__(self, package, save_dir):
        '''构造器
        :param str device: 设备
        :param str package : 包名
        :param timeout : logcat收集世家
        '''
        super().__init__()
        self.package = package
        self.save_dir = save_dir
        self.running = False  # logcat状态
        self.restart_lock = threading.Lock()
        self._stop_event = threading.Event()
        self.set_logcat_buffer("10M")  # 设置logcat的缓冲去，默认的特别小容易logcat容易崩溃
        self.clear_logcat_buffer()
        self.pid = None
        G.stop_event.set()

    def set_logcat_buffer(self, size):
        logcat_buffer_cmd = "logcat -G {}".format(size)
        logcat_buffer_cmd = G.device.adb.start_cmd(logcat_buffer_cmd, only_args=True)
        res = subprocess.run(logcat_buffer_cmd, capture_output=True, timeout=20)
        if res.returncode == 0:
            logger.info("logcat设置缓存成功")
        else:
            logger.info("logcat设置缓存失败，错误信息：{}".format(res.stderr))

    def clear_logcat_buffer(self):
        clear_logcat_buffer_cmd = "logcat -c"
        logcat_buffer_cmd = G.device.adb.start_cmd(clear_logcat_buffer_cmd, only_args=True)
        try:
            res = subprocess.run(logcat_buffer_cmd, capture_output=True, timeout=20)
        except subprocess.TimeoutExpired as e:
            logger.info("logcat清除缓存超时")
            return
        if res.returncode == 0:
            logger.info("logcat清除缓存成功")
        else:
            logger.info("logcat清除缓存失败，错误信息：{}".format(res.stderr))

    def start(self):
        super(Monitor, self).start()

    # 结束任务
    def stop(self):
        G.stop_event.clear()

    # 暂停任务
    def suspend(self):
        G.suspend_event.clear()

    def run(self):
        if G.stop_event.is_set():  # 只有还在运行中才启动logcat
            if not os.path.exists(self.save_dir):
                os.makedirs(self.save_dir)
            logcat_file = os.path.join(self.save_dir, LOGCAT_FILE_NAE)

            with open(logcat_file, "a+") as logcat_file:
                if self.running == True:
                    logger.warning(u'logcat process have started,not need start')
                    return
                if G.device.package_pid:
                    self.pid = G.device.package_pid
                else:
                    self.pid = G.device.get_pid()
                self.logcat_cmd = "logcat *:E".format(G.device.package_pid)
                self.logcat_cmd = G.device.adb.start_cmd(self.logcat_cmd, only_args=True)
                self.logcat_proc = subprocess.Popen(self.logcat_cmd, stdout=logcat_file, stderr=logcat_file)
                logger.info("启动logcat成功")
                self.running = True
                self._logcat_thread = threading.Thread(target=self._logcat_thead_func)
                self._logcat_thread.start()

    def _logcat_thead_func(self):
        self.logcat_proc.communicate()

    def restart(self):
        with self.restart_lock:  # logcat
            if not self.pid == G.device.package_pid:  # 只有pid不一样了才会重启logcat
                self.pid = G.device.package_pid
                self.stop()
                self.start()

    def stop_logcat(self):
        logger.info("进入stop_logcat函数")
        if self.running == True:
            self.running = False
            self.clear_logcat_buffer()
            logger.debug("stop logcat")
            # if hasattr(self, '_log_pipe'):
            if self.logcat_proc.poll() == None:  # 判断logcat进程是否存在
                self.logcat_proc.terminate()
            logcat_pid = self.get_logcat_pid()
            G.device.adb.killpid(logcat_pid)

    def get_logcat_pid(self):
        res = G.device.adb.raw_shell("ps | grep logcat|grep --pid={}".format(G.device.package_pid))
        try:
            pid = res.decode().split()[1]
        except Exception as e:
            pid = ""
            logger.info("logcat 获取pid发生异常:")
            logger.exception(e)
        logger.info("logcat 获取到的pid是{}".format(pid))
        return pid

    def save(self, save_file_path, loglist):
        monkey_file = os.path.join(save_file_path)
        with open(monkey_file, 'a+', encoding="utf-8") as log_f:
            for log in loglist:
                log_f.write(log + "\n")


#
# class LogcatIos(Monitor):
#     '''
#     logcat收集器
#     '''
#
#     def __init__(self, package, save_dir):
#         '''构造器
#         :param str device: 设备
#         :param str package : 包名
#         :param timeout : logcat收集世家
#         '''
#         self.package = package
#         self.save_dir = save_dir
#         self.running = False  # logcat状态
#         self.restart_lock = threading.Lock()
#         self._stop_event = threading.Event()
#
#     def start(self):
#         '''启动logcat
#         '''
#         self.start_logcat(self.package)
#
#     def stop(self):
#         '''结束logcat
#         '''
#         self.stop_logcat()
#
#     def start_logcat(self, package):
#         if not G.stop_event.is_set():  # 只有还在运行中才启动logcat
#             if not os.path.exists(self.save_dir):
#                 os.makedirs(self.save_dir)
#             logcat_file = os.path.join(self.save_dir, LOGCAT_FILE_NAE)
#
#             # with open(logcat_file,"a+") as logcat_file:
#             if self.running == True:
#                 logger.warning(u'ios logcat process have started,not need start')
#                 return
#             self.logcat_cmd = "syslog | grep {0}".format(package)
#             #  self.logcat_cmd = "logcat *:E --pid={}".format(G.device.package_pid)
#             self.logcat_proc = G.device.tidevice.cmd(self.logcat_cmd, is_block=False)
#             logger.info("ios 启动logcat成功")
#             self.running = True
#             self._logcat_thread = threading.Thread(target=self._logcat_thead_func, args=(logcat_file,))
#             # self._monkey_thread.setDaemon(True)
#             self._logcat_thread.start()
#
#     def _logcat_thead_func(self, logcat_file):
#         with open(logcat_file, 'a+', encoding="utf-8") as f:
#             while self.running:
#                 try:
#                     res = self.read_line()
#                 except FunctionTimedOut as e:
#                     logger.info(e)
#                     continue
#                 if res:
#                     f.write(res)
#             logger.info("end run")
#
#     def restart(self):
#         pass
#
#     @func_set_timeout(1)
#     def read_line(self):
#         return self.logcat_proc.readline()
#
#     def stop_logcat(self):
#         logger.info("进入stop_logcat函数")
#         if self.running == True:
#             self.running = False
#             logger.debug("ios stop logcat")
#             # if hasattr(self, '_log_pipe'):
#             try:
#                 self.logcat_proc.close()
#             except Exception as e:
#                 logger.debug("stop ios log err")
#         print(threading.enumerate())

#
if __name__ == "__main__":
    from device import AndroidDevice

    G.device = AndroidDevice(serialno="emulator-5554", server_addr=["localhost", "5037"],
                             package="com.road7.ddtdmxandroid.ld", save_dir="localhost")
    G.device.start_app()
    G.logcat = Logcat(package="com.road7.ddtdmxandroid.ld", save_dir="./")
    G.logcat.start()
    time.sleep(30)
#     # from device import AndroidDevice
#     # device=AndroidDevice(serialno="NCNNW21408002159",server_addr=["10.130.131.79","5039"],package="com.happyelements.es2", save_dir=r"C:\Users\happyelements\Desktop\tess.txt")
#     # device.start_collect_logcat()
#     # monkey = Monkey(device,package="com.happyelements.es2",save_dir='./')
#     # monkey.start()
#     # monkey.stop_monkey()
#     # G.device = AndroidDevice(serialno="NCNNW21408002159", server_addr=["10.130.131.79","5039"], package="com.happyelements.es2",
#     #                          save_dir="testlogcat.txt")
#     ios = IosDevice(serialno="00008030-001045603E50402E", device_addr="http://10.130.131.82:20001",
#                     package="com.happyelements.Sakicn", save_dir=".")
#     G.device = ios
#     G.logcat = LogcatIos(package="com.happyelements.es2", save_dir=".")
#     G.logcat.start()
#     time.sleep(10)
#     G.logcat.stop()
