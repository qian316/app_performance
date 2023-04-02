# coding=utf-8
import sys
sys.path.append("../")
import threading
import time
from builtins import *
from pathlib import Path

from airtest.core.android import Android

from performancetest.core.base.monitor import Monitor
from performancetest.core.global_data import GlobalData as G, logger


# # from config import PIC_TRUE_LOG
# from PIL import Image
# from func_timeout import func_set_timeout

class SnapshotMonitor(Monitor):
    def __init__(self, save_dir, serialno, server_addr, interval=1, test_time=-1):
        super().__init__()
        self.save_dir = self.get_save_file(save_dir)
        self.interval = interval
        self.device = Android(serialno, host=server_addr)

    def get_save_file(self, save_dir):
        save_dir = Path(save_dir)
        if not save_dir.is_dir():
            save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir

    def snapshot(self, name):
        self.device.snapshot(filename=name)

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
        按照指定频率手机截图
        '''
        logger.info("开始保存图片")
        G.stop_event.set()  # 启动
        G.suspend_event.set()  # 启动
        while G.stop_event.is_set():  # 停止了循环会停止
            G.suspend_event.wait()  # 暂停时会暂停在这里
            try:
                logger.debug(
                    "---------------开始截图, _collect_screenshot loop thread is : " + str(threading.current_thread().name))
                before = time.time()
                self.snapshot(self.save_dir.joinpath(str(int(before * 1000)) + ".jpg"))
                after = time.time()
                time_consume = after - before
                logger.debug("  ============== time consume snapshot time : " + str(time_consume))
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as e:
                logger.error("an exception hanpend in snapshot thread , reason unkown!, e:")
                logger.exception(e)
        logger.debug("snapshot stop")


# class IosSnapshotMonitor(Monitor):
#     def __init__(self, save_dir, serialno, host, port, package, interval=1, test_time=-1):
#         self.save_dir = self.get_save_file(save_dir)
#         self.interval = interval
#         wda.HTTP_TIMEOUT = 10.0  # default 60.0 seconds
#         self.dwa = wda.Client("http://" + ":".join([host, port]))
#         self.package = package
#         self.create_session()
#         self.screenshot_collect = threading.Thread(target=self._collect_screenshot, args=(test_time,))
#         self._stop_event = threading.Event()
#         self.running = False
#
#     @func_set_timeout(3)
#     def create_session(self):
#         self.session = self.dwa.session()
#
#     def get_save_file(self, save_dir):
#         save_dir = Path(save_dir).joinpath(PIC_TRUE_LOG)
#         if not save_dir.is_dir():
#             save_dir.mkdir(parents=True, exist_ok=True)
#         return save_dir
#
#     def snapshot(self, name):
#         try:
#             self.session.screenshot(name)
#             compress = CompressImg(str(name))
#             compress.compress_img_PIL()
#             os.rename(str(name), str(name).replace("png", "jpg"))
#         except Exception as e:
#             logger.error(e)
#             try:
#                 self.session.close()
#             except Exception as e:
#                 logger.error(e)
#             self.session = self.dwa.session()
#         # self.device.snapshot(filename=name)
#
#     def start(self):
#         self.screenshot_collect.start()
#
#     def stop(self):
#         self._stop_event.set()
#         try:
#             self.session.close()
#         except Exception as e:
#             logger.info("close wda")
#
#     def __del__(self):
#         try:
#             self.session.close()
#             self.dwa.close()
#         except:
#             pass
#
#     def _collect_screenshot(self, test_time):
#         '''
#         按照指定频率手机截图
#         '''
#         logger.info("开始保存图片")
#         G.monitor_pause.wait()
#         while not self._stop_event.is_set() and not G.stop_event.is_set():
#             try:
#                 logger.debug(
#                     "---------------开始截图, _collect_screenshot loop thread is : " + str(threading.current_thread().name))
#                 before = time.time()
#                 print(str(self.save_dir.joinpath(str(before * 1000))))
#                 self.snapshot(self.save_dir.joinpath(str(int(before * 1000)) + ".png"))
#                 after = time.time()
#                 time_consume = after - before
#                 logger.debug("  ============== time consume snapshot time : " + str(time_consume))
#                 delta_inter = self.interval - time_consume
#                 if delta_inter > 0:
#                     time.sleep(delta_inter)
#             except Exception as e:
#                 logger.error("an exception hanpend in snapshot thread , reason unkown!, e:")
#                 logger.exception(e)
#             G.monitor_pause.wait()
#         logger.debug("snapshot stop")
#
#
# class CompressImg(object):
#
#     def __init__(self, img_path):
#         self.img_path = img_path
#         self.img_name = img_path.split(os.sep)[-1]
#
#     def compress_img_PIL(self, way=1, compress_rate=0.3, show=False):
#         '''
#         img.resize() 方法可以缩小可以放大
#         img.thumbnail() 方法只能缩小
#         :param way:
#         :param compress_rate:
#         :param show:
#         :return:
#         '''
#         img = Image.open(self.img_path)
#         w, h = img.size
#         img_resize = img.resize((int(w * compress_rate), int(h * compress_rate)))
#         resize_w, resieze_h = img_resize.size
#         img_resize.save(self.img_path)


if __name__ == "__main__":
    s = SnapshotMonitor(save_dir=r"\home\report1\performance_test_result\192\295", serialno="emulator-5554",
                        host="localhost", port="5037")
    s.start()
    time.sleep(10)
    s.stop()
    # s = IosSnapshotMonitor(save_dir=r"\home\report1\performance_test_result\192\295", serialno="NAB0220B05000134",
    #                        host="10.130.131.82", port="20008", package="com.happyelements.Sakicn")
    # s.start()
