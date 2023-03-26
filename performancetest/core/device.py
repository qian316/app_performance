import logging
import os
import threading
from builtins import *

from func_timeout import func_set_timeout

from .command import ADB

# , Tidevice

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
import subprocess


class LogCatCollect(threading.Thread):
    def __init__(self, device):
        super.__init__(daemon=True)
        self.device = device

    def run(self):
        pid = self.device.get_pid()


class AndroidDevice(object):
    def __init__(self, serialno, server_addr, package, save_dir):
        self.adb = ADB(serialno=serialno, server_addr=server_addr)
        self.serialno = serialno
        self.server_addr = server_addr
        self.package_pid = ''
        self.package = package
        self.save_dir = save_dir
        self.collect_logcat = threading.Thread(target=self._collect_logcat)
        self.sdkversion = self.get_sdkversion()

    def get_sdkversion(self):
        sdkversion = self.adb.raw_shell("getprop ro.build.version.sdk")
        logger.info("获取到的sdk版本号是{}".format(sdkversion))
        sdkversion = sdkversion.decode().strip()
        if sdkversion:
            return int(sdkversion)
        else:
            # 没有获取到sdkverison默认返回25
            return 25

    def get_front_app(self):
        lines: str = self.adb.raw_shell("dumpsys activity top | grep ACTIVITY").decode()
        logger.info("获取到的activty是{0}".format(lines))
        return lines.strip()

    def app_is_front(self):
        lines = self.get_front_app()
        lines = lines.split(os.linesep)
        for line in lines:
            if self.package in line:
                break
        else:
            raise Exception("app未启动")
        return (self.package in lines[-1]) and ("WebLandActivity" not in lines[-1]) and (
                "ali" not in lines[-1].lower()) and ("wx" not in lines[-1].lower())

    def get_packgelist(self):
        stdout = self.adb.raw_shell("pm list package")
        return stdout

    def is_install_package(self, package):
        stdout = self.adb.raw_shell("pm list package")
        logger.info("pm list package 返回内容：{0}".format(str(stdout)))
        if stdout.decode().find("package:" + package + os.linesep) > -1:
            return True
        else:
            return False

    def start_collect_logcat(self):
        self.collect_logcat.start()

    def _collect_logcat(self):
        with open(os.path.join(self.save_dir, "logcat.txt"), "w+") as f:
            pid = self.get_pid()
            collect_cmd = "adb logcat --pid=={}".format(pid)
            subprocess.run(collect_cmd.split(" "), stdout=f, stderr=f)

    def install_apk(self, apk_route):
        self.adb.raw_shell(["adb", "install", apk_route])

    @func_set_timeout(5)
    def stop_app(self):
        self.adb.raw_shell(["am", "force-stop", self.package])

    def start_app(self):  # 启动app
        self.adb.raw_shell(['monkey', '-p', self.package, '-c', 'android.intent.category.LAUNCHER', '1'])

    def get_pid(self):
        try:
            pid_infos = self.adb.raw_shell("ps | grep " + self.package).decode()
            real_pid = None
            pid_infos = pid_infos.splitlines()
            for pid in pid_infos:
                if pid.split()[-1] == self.package:
                    real_pid = pid.split()[1]
            if not real_pid:
                real_pid = pid_infos.split()[1]
            logger.info("测试包获取到的pid是{}".format(real_pid))
            self.package_pid = real_pid
            return real_pid
        except IndexError as e:
            logger.error("获取到的pid信息是{}".format(pid_infos))
            logger.exception(e)


# class IosDevice(object):
#     def __init__(self, serialno, device_addr, package, save_dir):
#         self.tidevice = Tidevice(serialno=serialno, device_addr=device_addr, tidevice_path=IOSPYTHON + " -m tidevice")
#         self.serialno = serialno
#         self.device_addr = device_addr
#         self.package_pid = ''
#         self.package = package
#         self.save_dir = save_dir
#         if not self.is_install_package():
#             raise Exception("设备没有安装对应的包{0}，结束运行".format(self.package))
#         # self.collect_logcat = threading.Thread(target=self._collect_logcat)
#
#     def is_install_package(self):
#         stdout = self.tidevice.raw_shell("applist")
#         logger.info("pm list package 返回内容：{0}".format(str(stdout.decode())))
#         lines = stdout.decode().strip()
#         for i in lines.split():
#             if self.package in i:
#                 return True
#         else:
#             return False
#
#     def start_app(self):  # 启动app
#         self.tidevice.raw_shell(['launch', self.package])
#
#     def stop_app(self):
#         self.tidevice.raw_shell(["kill", self.package])
#
#     def get_pid(self):
#         pass


if __name__ == '__main__':
    device = AndroidDevice(serialno="99392a4c", server_addr=["localhost", "5037"], package="com.tencent.tmgp.sgame",
                           save_dir="./test")
    device.start_app()
    pid = device.get_pid()
    print(pid)
    # ios = IosDevice(serialno="00008110-0002398A36B8801E", device_addr="10.130.131.82:20020?mjpeg_port=20021", package="com.happyelements.Sakicn", save_dir="")
    # is_install_apk = ios.is_install_package()
    # print(is_install_apk)
    # ios.start_app()
    # time.sleep(4)
    # ios.stop_app()
    # time.sleep(10)
    # print("end")
