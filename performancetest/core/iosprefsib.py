# # coding=utf-8
# import csv
# import json
# import logging
# import os
# import sys
# import threading
# import time
# import traceback
#
# from func_timeout import func_set_timeout, FunctionTimedOut
#
# sys.path.append(".")
# from performancetest.core.base.monitor import Monitor
# import sys
#
# sys.path.append(".")
# from global_data import GlobalData as G
#
# logger = logging.getLogger(__file__)
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
#
#
# class IosPerfSibMonitor(Monitor):
#     def __init__(self, save_dir):
#         self.save_dir = save_dir
#         self._stop_event = threading.Event()
#         # self.ios_perf_collect = [
#         #                          threading.Thread(target=self._collect_package_ios_perf_battery_thread, args=(test_time,)),
#         #                          threading.Thread(target=self._collect_package_ios_perf_cpu_thread, args=(test_time,))
#         #                          ]
#         self.pid = None
#         self.interval = 1
#         self.is_front = False
#         self.should_close_instance = []
#         self.property_all = {
#             "cpu": (os.path.join(self.save_dir, "cpu.csv"), ["timestamp", "cpu%"]),
#             "memory": (os.path.join(self.save_dir, "memory.csv"), ["timestamp", "memory"]),
#             "fps": (os.path.join(self.save_dir, "fps.csv"),
#                     ["timestamp", "FPS", "lag_number", "FPS_full_number", "jank_number", "big_jank_number"]),
#             "gpu": (os.path.join(self.save_dir, "gpu.csv"), ["timestamp", "gpu%"]),
#             "devicebattery": (os.path.join(self.save_dir, "devicebattery.csv"),
#                               ["timestamp", "devicetemperature", "devicebatterylevel", "charge"])
#         }
#         self.monitor_ps_thread = threading.Thread(target=self._process_is_exists_thread)
#         self.ios_perf_collect = [
#             threading.Thread(target=self._collect_package_ios_perf_cpu_thread),
#             threading.Thread(target=self._collect_package_ios_perf_memory_thread),
#             threading.Thread(target=self._collect_package_ios_perf_fps_thread),
#             threading.Thread(target=self._collect_package_ios_perf_gpu_thread),
#             threading.Thread(target=self._collect_package_ios_perf_battery_thread)
#         ]
#         for k, v in self.property_all.items():
#             with open(v[0], 'w+') as df:
#                 print('-------------------初始csv')
#                 csv.writer(df, lineterminator='\n').writerow(v[1])
#
#     def get_perf_info(self, target_o=None):
#         """
#             target_o:  cpu, mem, gpu, fps
#         """
#
#         if not target_o:
#             cmds = ["perfmon", "-b", G.device.package, '-j']
#         else:
#             if target_o in ['cpu', 'mem']:
#                 target = '--proc-' + target_o
#             else:
#                 target = '--' + target_o
#             cmds = ["perfmon", "-b", G.device.package, target, '-j']
#         logger.info("get_perf_info {0}".format(cmds))
#         print('cmd  before')
#         stdout = G.device.device.cmd(cmds, block=False)
#         print('cmd  after')
#         self.should_close_instance.append(stdout)
#         return stdout
#
#     # @func_set_timeout(3)
#     def get_battery(self):
#         cmds = ["battery", '-j']
#         logger.info("get_battery_info {0}".format(cmds))
#         stdout = G.device.device.cmd(cmds, timeout=1)
#         battery_info = stdout.decode()
#         logger.info("get_battery_info {0}".format(battery_info))
#         battery_info = json.loads(battery_info)
#         battery_info_res = dict()
#         battery_info_res['battery'] = battery_info['CurrentCapacity']
#         battery_info_res['level'] = battery_info['Temperature'] / 100
#         return battery_info_res
#
#     def start(self):
#         # to do 后续监控进程是否存在  来重启线程
#         # self.monitor_ps_thread.start()
#         for th in self.ios_perf_collect:
#             th.start()
#
#     def stop(self):
#         self._stop_event.set()
#
#     # 后续解决杀掉游戏  重启各线程读取性能数据流
#     def _process_is_exists_thread(self):
#         while not G.stop_event.is_set():
#             if self.pid:
#                 # window上是findstr  linux上是grep
#                 psInfo = G.device.device.cmd([f'ps | findstr /RC:" {self.pid} "'], block=True, shell=True,
#                                              single_cmd=True)
#                 print('----------psInfo:', psInfo.decode())
#                 if not psInfo.decode():
#                     self.stop()
#                     self._wait_other_thread()
#                     self.__del__()
#                     self._start_perf_thread()
#                     self.pid = None
#             print('listening ....')
#             time.sleep(5)
#
#     def _wait_other_thread(self):
#         for th in self.ios_perf_collect:
#             th.join()
#
#     def _start_perf_thread(self):
#         # 线程对象不能start两次
#         self.ios_perf_collect = [
#             threading.Thread(target=self._collect_package_ios_perf_cpu_thread),
#             threading.Thread(target=self._collect_package_ios_perf_memory_thread),
#             threading.Thread(target=self._collect_package_ios_perf_fps_thread),
#             threading.Thread(target=self._collect_package_ios_perf_gpu_thread),
#             threading.Thread(target=self._collect_package_ios_perf_battery_thread)
#         ]
#         # 重新初始化signal信号量
#         self._stop_event.clear()
#         for th in self.ios_perf_collect:
#             th.start()
#
#     def _collect_package_ios_perf_cpu_thread(self):
#         print('cpu start')
#         before = time.time()
#         G.monitor_pause.wait()
#         stdout = self.get_perf_info("cpu")
#         count = 0
#         while not self._stop_event.is_set() and not G.stop_event.is_set():
#             print('cpu loop...')
#             try:
#                 logging.debug("---------------开始获取性能信息" + str(
#                     threading.current_thread().name))
#                 # line = stdout.readline()
#                 try:
#                     line = self.read_line(stdout)  # 可超时的任务
#                     after = time.time()
#                     time_consume = after - before
#                 except FunctionTimedOut as e:
#                     logging.error(e)
#                     continue
#                 logging.info("---iosperf 获取到数据 {0}".format(line))
#                 delta_inter = self.interval - time_consume
#                 if delta_inter > 0:
#                     time.sleep(delta_inter)
#                 write_info = []
#                 try:
#                     data_res = json.loads(line.decode())
#                 except Exception as e:
#                     logging.info(line.decode() + "can't parse json..")
#                     cpu_value = 0
#                     timestp = int(time.time())
#                     self.is_front = False
#                 else:
#                     timestp = int(data_res.get("timestamp", 0))
#                     cpu_value = data_res.get("proc_perf", {}).get("cpuUsage", 0)
#                     if cpu_value > 0.01:
#                         self.is_front = True
#                     else:
#                         self.is_front = False
#                     if not self.pid:
#                         self.pid = data_res.get("pid")
#                 write_info.append(timestp)
#                 write_info.append(cpu_value)
#
#                 file_path = self.property_all.get('cpu', None)
#                 if not file_path:
#                     continue
#                 if G.monitor_pause.is_set():
#                     with open(file_path[0], 'a+', encoding="utf-8") as df:
#                         logging.info("write {0}".format(write_info))
#                         csv.writer(df, lineterminator='\n').writerow(write_info)
#                         count += 1
#                         print('-----------write cpu  ', count)
#                         del write_info[:]
#             except Exception as e:
#                 logging.error("an exception hanpend in ios perf thread , reason unkown!, e: iosperf cpu")
#                 logging.error(e)
#                 logging.error(traceback.format_exc())
#             logging.error("not self._stop_event.is_set(): {0}  not G.stop_event.is_set(): {1} cpu".format(
#                 not self._stop_event.is_set(), not G.stop_event.is_set()))
#         logging.debug("stop event is set or timeout iosperf")
#
#     def _collect_package_ios_perf_memory_thread(self):
#         print('memory start')
#         G.monitor_pause.wait()
#         stdout = self.get_perf_info("mem")
#         last_value = 0
#         count = 0
#         while not self._stop_event.is_set() and not G.stop_event.is_set():
#             print('memory loop...')
#             before = time.time()
#             try:
#                 logging.debug("---------------开始获取性能信息" + str(
#                     threading.current_thread().name))
#                 # line = stdout.readline()
#                 try:
#                     line = self.read_line(stdout)  # 可超时的任务
#                     after = time.time()
#                     time_consume = after - before
#                 except FunctionTimedOut as e:
#                     logging.error(e)
#                     continue
#                 logging.info("---iosperf 获取到数据 {0}".format(line))
#                 delta_inter = self.interval - time_consume
#                 if delta_inter > 0:
#                     time.sleep(delta_inter)
#                 write_info = []
#                 try:
#                     data_res = json.loads(line.decode())
#                 except Exception as e:
#                     # json无法解析的情况 初始的前几行以及未启动app的情况
#                     logging.info(line.decode() + "can't parse json..")
#                     mem_value = 0
#                     timestp = int(time.time())
#                 else:
#                     # 可解析为json的情况  包括正常获取以及pid not found的情况
#                     timestp = int(data_res.get("timestamp", 0))
#                     mem_value = data_res.get("proc_perf", {}).get("physFootprint", 0)
#                     if not self.is_front:
#                         mem_value = 0
#                     else:
#                         if 'msg' in data_res:
#                             mem_value = last_value
#                         else:
#                             last_value = mem_value
#
#                 write_info.append(timestp)
#                 write_info.append(mem_value)
#                 file_path = self.property_all.get('memory', None)
#                 if not file_path:
#                     continue
#                 if G.monitor_pause.is_set():
#                     with open(file_path[0], 'a+', encoding="utf-8") as df:
#                         logging.info("write {0}".format(write_info))
#                         csv.writer(df, lineterminator='\n').writerow(write_info)
#                         count += 1
#                         print('--------write mem  ', count)
#                         del write_info[:]
#             except Exception as e:
#                 logging.error("an exception hanpend in ios perf thread , reason unkown!, e: iosperf memory")
#                 logging.error(e)
#                 logging.error(traceback.format_exc())
#             logging.error("not self._stop_event.is_set(): {0}  not G.stop_event.is_set(): {1} memory".format(
#                 not self._stop_event.is_set(), not G.stop_event.is_set()))
#         logging.debug("stop event is set or timeout iosperf")
#
#     def _collect_package_ios_perf_fps_thread(self):
#         print('fps start')
#         G.monitor_pause.wait()
#         stdout = self.get_perf_info("fps")
#         count = 0
#         while not self._stop_event.is_set() and not G.stop_event.is_set():
#             print('fps loop...')
#             before = time.time()
#             try:
#                 logging.debug("---------------开始获取性能信息" + str(
#                     threading.current_thread().name))
#                 # line = stdout.readline()
#                 try:
#                     line = self.read_line(stdout)  # 可超时的任务
#                     after = time.time()
#                     time_consume = after - before
#                 except FunctionTimedOut as e:
#                     logging.error(e)
#                     continue
#                 logging.info("---iosperf 获取到数据 {0}".format(line))
#
#                 delta_inter = self.interval - time_consume
#                 if delta_inter > 0:
#                     time.sleep(delta_inter)
#                 write_info = []
#                 try:
#                     data_res = json.loads(line.decode())
#                 except Exception as e:
#                     logging.info(line.decode() + "can't parse json..")
#                     fps_value = 0
#                     timestp = int(time.time())
#                 else:
#                     timestp = int(data_res.get("timestamp", 0))
#                     fps_value = data_res.get("fps", 0)
#
#                 write_info.append(timestp)
#                 write_info.append(fps_value)
#
#                 file_path = self.property_all.get('fps', None)
#                 if not file_path:
#                     continue
#                 if G.monitor_pause.is_set():
#                     with open(file_path[0], 'a+', encoding="utf-8") as df:
#                         logging.info("write {0}".format(write_info))
#                         csv.writer(df, lineterminator='\n').writerow(write_info)
#                         count += 1
#                         print('-----------write fps  ', count)
#                         del write_info[:]
#             except Exception as e:
#                 logging.error("an exception hanpend in ios perf thread , reason unkown!, e: iosperf fps")
#                 logging.error(e)
#                 logging.error(traceback.format_exc())
#             logging.error("not self._stop_event.is_set(): {0}  not G.stop_event.is_set(): {1} fps".format(
#                 not self._stop_event.is_set(), not G.stop_event.is_set()))
#         logging.debug("stop event is set or timeout iosperf")
#
#     def _collect_package_ios_perf_gpu_thread(self):
#         print('gpu start')
#         G.monitor_pause.wait()
#         stdout = self.get_perf_info("gpu")
#         count = 0
#         while not self._stop_event.is_set() and not G.stop_event.is_set():
#             print('gpu loop...')
#             before = time.time()
#             try:
#                 logging.debug("---------------开始获取性能信息" + str(
#                     threading.current_thread().name))
#                 # line = stdout.readline()
#                 try:
#                     line = self.read_line(stdout)  # 可超时的任务
#                     after = time.time()
#                     time_consume = after - before
#                 except FunctionTimedOut as e:
#                     logging.error(e)
#                     continue
#                 logging.info("---iosperf 获取到数据 {0}".format(line))
#
#                 delta_inter = self.interval - time_consume
#                 if delta_inter > 0:
#                     time.sleep(delta_inter)
#                 write_info = []
#                 try:
#                     data_res = json.loads(line.decode())
#                 except Exception as e:
#                     logging.info(line.decode() + "can't parse json..")
#                     gpu_value = 0
#                     timestp = int(time.time())
#                 else:
#                     timestp = int(data_res.get("timestamp", 0))
#                     gpu_value = data_res.get("device_utilization", 0)
#
#                 write_info.append(timestp)
#                 write_info.append(gpu_value)
#
#                 file_path = self.property_all.get('gpu', None)
#                 if not file_path:
#                     continue
#
#                 if G.monitor_pause.is_set():
#                     with open(file_path[0], 'a+', encoding="utf-8") as df:
#                         logging.info("write {0}".format(write_info))
#                         csv.writer(df, lineterminator='\n').writerow(write_info)
#                         count += 1
#                         print('-----------write gpu  ', count)
#                         del write_info[:]
#             except Exception as e:
#                 logging.error("an exception hanpend in ios perf thread , reason unkown!, e: iosperf gpu")
#                 logging.error(e)
#                 logging.error(traceback.format_exc())
#             logging.error("not self._stop_event.is_set(): {0}  not G.stop_event.is_set(): {1} gpu".format(
#                 not self._stop_event.is_set(), not G.stop_event.is_set()))
#         logging.debug("stop event is set or timeout iosperf")
#
#     def _collect_package_ios_perf_battery_thread(self):
#         print('battery start')
#         G.monitor_pause.wait()
#         count = 0
#         while not self._stop_event.is_set() and not G.stop_event.is_set():
#             print('battery loop...')
#             before = time.time()
#             try:
#                 logging.debug("---------------开始获取性能信息" + str(
#                     threading.current_thread().name))
#                 try:
#                     battery_level_dict = self.get_battery()
#                     after = time.time()
#                     time_consume = after - before
#                 except Exception as e:
#                     logging.error(e)
#                     continue
#                 delta_inter = self.interval - time_consume
#                 if delta_inter > 0:
#                     time.sleep(delta_inter)
#                 write_info = []
#                 write_info.append(int(time.time()))
#                 write_info.append(battery_level_dict.get("level"))
#                 write_info.append(battery_level_dict.get("battery"))
#                 write_info.append("true")
#
#                 if G.monitor_pause.is_set():
#                     with open(self.property_all.get("devicebattery")[0], 'a+', encoding="utf-8") as df:
#                         logging.info("write devicebattery {0}".format(write_info))
#                         csv.writer(df, lineterminator='\n').writerow(write_info)
#                         count += 1
#                         print("write  battery ", count)
#                         del write_info[:]
#             except Exception as e:
#                 logging.error("an exception hanpend in ios perf thread , reason unkown!, e: iosperf battery")
#                 logging.error(e)
#                 logging.error(traceback.format_exc())
#             logging.error("not self._stop_event.is_set(): {0}  not G.stop_event.is_set(): {1} battery".format(
#                 not self._stop_event.is_set(), not G.stop_event.is_set()))
#         logging.debug("stop event is set or timeout iosperf")
#
#     @func_set_timeout(3)
#     def read_line(self, stdout):
#         return stdout.readline()
#
#     def __del__(self):
#         for i in self.should_close_instance:
#             try:
#                 i.close()
#             except Exception as e:
#                 logging.error(e)
#
#
# if __name__ == "__main__":
#     from device import IosDevice
#
#     ios = IosDevice(serialno="8bc12249866767388b0dcfff4e58931d474d4054", device_addr="10.131.129.128",
#                     package="com.happyelements.1OSAnimal", save_dir=".", is_local_device=True)
#     G.device = ios
#     ios.start_app()
#     iosp = IosPerfSibMonitor(".")
#     iosp.start()
#     time.sleep(2 * 10)
#     # stdout = iosp.get_perf_info('cpu')
#     # stdout = iosp.get_battery()
#     # print(stdout)
#     time.sleep(5)
#     # ios.stop_app()
#     # time.sleep(10)
#     # iosp.stop()
