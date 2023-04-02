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

_lock = threading.Lock()


class ParsFPSInfo(object):
    FPS_queue: list = []  # FPS collect, 每个帧对象的结果都汇集在这里，这里每次只留最后一个不完整的帧
    before_time: list = []  # 存第一秒前3帧的
    PHONE_REAL_TIME_INTERVAL: int = None  # 真实时间和手机时间的相对差值
    start_collect_time: float = None  # 开始时间测试的真实时间

    def __init__(self, surface_info):
        with _lock:
            logger.info("star instance {0}".format(ParsFPSInfo.FPS_queue))
            self.lag_number = 0  # 每秒小于24帧的次数
            self.FTIMEGE100 = 0  # 增量耗时
            self.surface_info = surface_info
            self.jank_number = [0]
            self.big_jank_number = [0]
            self.front_FPS_list = []  # 第一个完整的秒的 FPS
            self.FPS_res_info_dict: dict = {}  # 真正返回的FPS结果集 {时间：帧信息, 时间+1s: 帧信息}
            self.FPS = self.get_FPS()
            logger.info("end instance {0}".format(ParsFPSInfo.FPS_queue))

    def get_FPS(self):
        surface_info_resource = self.surface_info.split(os.linesep)
        new_FPS: tuple = self._GetSurfaceFlingerFrameData(surface_info_resource)
        self.add_new_FPS(new_FPS[1])
        logger.info("end get new fps")
        self.get_front_FPS()
        logger.info("log get fps result")
        logger.info(ParsFPSInfo.FPS_queue)
        full_FPS_number = int(1 / new_FPS[0])
        self.full_FPS_number = full_FPS_number
        # return min(full_FPS_number, len(self.front_FPS_list))
        return self.FPS_res_info_dict

    def add_new_FPS(self, new_FPS):
        if ParsFPSInfo.FPS_queue:
            FPS_list_last = ParsFPSInfo.FPS_queue[-1]
            for index, v in enumerate(new_FPS):
                if v == FPS_list_last:
                    self.FPS_queue.extend(new_FPS[index + 1:])
                    logger.info("find result")
                    logger.info("剩余帧{0}".format(len(ParsFPSInfo.FPS_queue)))
                    break
            else:
                if new_FPS and FPS_list_last < new_FPS[0]:
                    ParsFPSInfo.FPS_queue.extend(new_FPS)
                else:
                    logger.error("丢帧！！！！！！！！！！！！！！！！！！！！！！！！！！！！")
                    logger.error(FPS_list_last)
                    logger.error(new_FPS)
            if not ParsFPSInfo.PHONE_REAL_TIME_INTERVAL:
                if len(new_FPS) > 126 and new_FPS[-1] != 0.0:
                    ParsFPSInfo.PHONE_REAL_TIME_INTERVAL = int(time.time()) - new_FPS[-1]
                    logger.info("时间间隔-new-{0}, {1}".format(ParsFPSInfo.PHONE_REAL_TIME_INTERVAL, new_FPS[-1]))
        else:
            ParsFPSInfo.FPS_queue.extend(new_FPS)
            if not ParsFPSInfo.PHONE_REAL_TIME_INTERVAL:
                first_time = 0.0  # 拿到第一个有值的数据和真实时间对应
                for i in ParsFPSInfo.FPS_queue:
                    if float(i) != 0.0 and first_time == 0.0:
                        first_time = i
                logger.info("first_time {0}".format(first_time))
                if first_time != 0.0:
                    if ParsFPSInfo.start_collect_time:
                        ParsFPSInfo.PHONE_REAL_TIME_INTERVAL = ParsFPSInfo.start_collect_time - int(first_time)
                        # ParsFPSInfo.start_collect_time = None, 不会中断开始收集时间有一个就够了
                    else:
                        ParsFPSInfo.PHONE_REAL_TIME_INTERVAL = int(time.time()) - int(first_time)
                    logger.info(
                        "时间间隔 {0} {1} {2} {3}".format(ParsFPSInfo.PHONE_REAL_TIME_INTERVAL, time.time(), first_time,
                                                      ParsFPSInfo.FPS_queue))
                else:
                    ParsFPSInfo.FPS_queue = []
                    ParsFPSInfo.PHONE_REAL_TIME_INTERVAL = None
                    logger.info("第一个时间戳有误")
                    logger.info(ParsFPSInfo.FPS_queue)

    def get_front_FPS(self):
        """
        PerfDog Jank计算方法：
        同时满足两条件，则认为是一次卡顿Jank.
        ①Display FrameTime>前三帧平均耗时2倍。
        ②Display FrameTime>两帧电影帧耗时 (1000ms/24*2=84ms)。
        同时满足两条件，则认为是一次严重卡顿BigJank.
        ①Display FrameTime >前三帧平均耗时2倍。
        ②Display FrameTime >三帧电影帧耗时(1000ms/24*3=125ms)。
        """
        # 拿到了队列里所有的完整帧
        while ParsFPSInfo.FPS_queue:
            logger.info("join get front fps")
            tmp = []
            time_flag = ParsFPSInfo.FPS_queue.pop(0)
            time_second = int(time_flag)
            tmp.append(time_flag)
            while ParsFPSInfo.FPS_queue and int(ParsFPSInfo.FPS_queue[0]) == time_second:
                header_ele = ParsFPSInfo.FPS_queue.pop(0)
                tmp.append(header_ele)
            if not ParsFPSInfo.FPS_queue:
                ParsFPSInfo.FPS_queue.extend(tmp)
                break
            else:
                self.front_FPS_list.append(tmp)
        res_dict = {}
        try:
            for item_list in self.front_FPS_list:
                # print(item_list[0], ParsFPSInfo.PHONE_REAL_TIME_INTERVAL)
                # 如果当前帧都是空就跳过
                if sum(item_list) == 0.0:
                    continue
                first_time_head = None  # 获取第一个帧第一个有时间的值
                for time_head in item_list:
                    first_time_head = time_head if time_head else None
                res_dict[int(first_time_head) + ParsFPSInfo.PHONE_REAL_TIME_INTERVAL] = item_list[0:]
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
        self.FPS_res_info_dict: dict = res_dict
        self.get_jank(self.FPS_res_info_dict)

    def get_jank(self, FPS_res_info_dict: dict):
        for front_index, (time_number, item_list_v) in enumerate(FPS_res_info_dict.items()):
            for index, v in enumerate(item_list_v):
                if len(ParsFPSInfo.before_time) < 4:
                    ParsFPSInfo.before_time.append(v)
                else:
                    interval = v - ParsFPSInfo.before_time[-1]
                    if interval > 0.1:
                        ParsFPSInfo.FTIMEGE100 = 1
                    else:
                        ParsFPSInfo.FTIMEGE100 = 0
                    if v - ParsFPSInfo.before_time[-1] > sum([
                        ParsFPSInfo.before_time[-1] - ParsFPSInfo.before_time[-2],
                        ParsFPSInfo.before_time[-2] - ParsFPSInfo.before_time[-3],
                        ParsFPSInfo.before_time[-3] - ParsFPSInfo.before_time[-4], ]) / 3 * 2:
                        if interval > 0.125:
                            if len(self.big_jank_number) <= front_index:
                                self.big_jank_number.append(1)
                            else:
                                self.big_jank_number[front_index] += 1
                        elif interval > 0.084:
                            if len(self.jank_number) <= front_index:
                                self.jank_number.append(1)
                            else:
                                self.jank_number[front_index] += 1
                    ParsFPSInfo.before_time.pop(0)
                    ParsFPSInfo.before_time.append(v)

    def _GetSurfaceFlingerFrameData(self, results):
        """Returns collected SurfaceFlinger frame timing data.

        Returns:
          A tuple containing:
          - The display's nominal refresh period in seconds.
          - A list of timestamps signifying frame presentation times in seconds.
          The return value may be (None, None) if there was no data collected (for
          example, if the app was closed before the collector thread has finished).
        """
        # adb shell dumpsys SurfaceFlinger --latency <window name>
        # prints some information about the last 128 frames displayed in
        # that window.
        # The data returned looks like this:
        # 16954612
        # 7657467895508   7657482691352   7657493499756
        # 7657484466553   7657499645964   7657511077881
        # 7657500793457   7657516600576   7657527404785
        # (...)
        #
        # The first line is the refresh period (here 16.95 ms), it is followed
        # by 128 lines w/ 3 timestamps in nanosecond each:
        # A) when the app started to draw
        # B) the vsync immediately preceding SF submitting the frame to the h/w
        # C) timestamp immediately after SF submitted that frame to the h/w
        #
        # The difference between the 1st and 3rd timestamp is the frame-latency.
        # An interesting data is when the frame latency crosses a refresh period
        # boundary, this can be calculated this way:
        #
        # ceil((C - A) / refresh-period)
        #
        # (each time the number above changes, we have a "jank").
        # If this happens a lot during an animation, the animation appears
        # janky, even if it runs at 60 fps in average.
        #
        # We use the special "SurfaceView" window name because the statistics for
        # the activity's main window are not updated when the main web content is
        # composited into a SurfaceView.
        timestamps = []
        if not len(results):
            return (None, None)

        # 针对oppo Find 2x 的一款手机兼容
        if "TIME" in results[0]:
            results = results[1:]

        nanoseconds_per_second = 1e9
        refresh_period = int(results[0]) / nanoseconds_per_second

        # If a fence associated with a frame is still pending when we query the
        # latency data, SurfaceFlinger gives the frame a timestamp of INT64_MAX.
        # Since we only care about completed frames, we will ignore any timestamps
        # with this value.
        pending_fence_timestamp = (1 << 63) - 1

        for index, line in enumerate(results[1:]):
            fields = line.split()
            if len(fields) != 3:
                continue
            try:
                timestamp = int(fields[1])
            except ValueError as e:
                logger.error(e)
                continue
            if timestamp == pending_fence_timestamp:
                continue
            timestamp /= nanoseconds_per_second
            # if index == 0:
            #     for _, v in enumerate(timestamps):
            #         if v == timestamp:
            #             timestamps = timestamps[:_]
            #             break
            timestamps.append(timestamp)
        return (refresh_period, timestamps)


class FPSMonitor(Monitor):
    def __init__(self, save_file, interval=1, test_time=-1):
        super().__init__()
        self.save_file = save_file
        self._stop_event = threading.Event()
        self.interval = interval
        self.m_surface_view_name = None

    def get_FPS_info(self):
        """
        通过执行 "dumpsys SurfaceFlinger --list" 命令，您可以获取有关当前正在显示在屏幕上的所有图形元素的详细信息，例如它们的名称、大小、格式、位置和可见性等。
        """
        surface_list_info = G.device.adb.raw_shell("dumpsys SurfaceFlinger --list").decode()
        self.get_FPS_surface_view(surface_list_info)
        """
        通过执行 "dumpsys SurfaceFlinger --latency" 命令，您可以获取有关SurfaceFlinger处理每一帧图像所需的时间的信息，包括处理时间的最小值、最大值、平均值和标准差等。
        """
        surface_info = G.device.adb.raw_shell(
            "dumpsys SurfaceFlinger --latency '{0}' ".format(self.m_surface_view_name)).decode()
        pars_FPS_info = ParsFPSInfo(surface_info)
        self.FPS_info = pars_FPS_info
        return pars_FPS_info.FPS, pars_FPS_info.lag_number, pars_FPS_info.full_FPS_number,

    def get_FPS_surface_view(self, surface_info):
        for i in surface_info.split(os.linesep):
            if "SurfaceView" not in i:
                continue
            if "Background for" in i:
                continue
            if G.device.package not in i:
                continue
            if not self.m_surface_view_name or "BLAST" in i:
                self.m_surface_view_name = i
        logger.info("获取到的surface_view信息是：{}".format(self.m_surface_view_name))

    def start(self):
        super(Monitor, self).start()

    # 结束任务
    def stop(self):
        G.stop_event.clear()

    # 暂停任务
    def suspend(self):
        G.suspend_event.clear()

    def run(self):
        G.device.adb.raw_shell("dumpsys SurfaceFlinger --latency-clear").decode()
        '''
        按照指定频率，循环搜集FPS的信息
        '''
        # ftimege100:增量耗时
        FPS_title = ["timestamp", "FPS", "lag_number", "FPS_full_number", "jank_number", "big_jank_number",
                     "ftimege100"]
        FPS_file = self.save_file
        with open(FPS_file, 'w+') as df:
            csv.writer(df, lineterminator='\n').writerow(FPS_title)
        G.stop_event.set()  # 启动
        G.suspend_event.set()  # 启动
        ParsFPSInfo.start_collect_time = int(time.time())
        while G.stop_event.is_set():  # 停止了循环会停止
            G.suspend_event.wait()  # 暂停时会暂停在这里
            FPS_list = []
            try:
                logger.debug("---------------开始获取手机fps信息, into _collect_package_FPS_thread loop thread is : " + str(
                    threading.current_thread().name))
                before = time.time()
                try:
                    FPS_info_FPS, FPS_info_lag_number, FPS_full_number = self.get_FPS_info()
                except Exception as e:
                    FPS_info_FPS, FPS_info_lag_number, FPS_full_number = {int(time.time()): []}, 0, 0
                    logger.info(e)
                finally:
                    if not FPS_info_FPS:
                        FPS_info_FPS = {int(time.time()): []}
                logger.info(
                    "fps collect result {0} {1} {2}".format(FPS_info_FPS, FPS_info_lag_number, FPS_full_number))
                after = time.time()
                time_consume = after - before
                logger.debug("  ============== time consume for fps info : " + str(time_consume))
                for front_index, (time_item, item_value_list) in enumerate(FPS_info_FPS.items()):
                    FPS_list.append(time_item)
                    FPS_list.append(len(item_value_list) if len(item_value_list) < FPS_full_number else FPS_full_number)
                    FPS_list.append(1 if len(item_value_list) < 24 else 0)
                    FPS_list.append(FPS_full_number)
                    try:
                        FPS_list.append(
                            self.FPS_info.jank_number[front_index] if len(
                                self.FPS_info.jank_number) > front_index else 0)
                    except Exception as e:
                        FPS_list.append(0)
                        logger.info(e)
                    try:
                        FPS_list.append(self.FPS_info.big_jank_number[front_index] if len(
                            self.FPS_info.big_jank_number) > front_index else 0)
                    except Exception as e:
                        FPS_list.append(0)
                        logger.info(e)
                    try:
                        FPS_list.append(ParsFPSInfo.FTIMEGE100)
                    except Exception as e:
                        FPS_list.append(0)
                        logger.info(e)
                    logger.info(FPS_file + "*****************************")
                    with open(FPS_file, 'a+', encoding="utf-8") as df:
                        csv.writer(df, lineterminator='\n').writerow(FPS_list)
                        del FPS_list[:]
                    delta_inter = self.interval - time_consume
                    if delta_inter > 0:
                        time.sleep(delta_inter)
            except Exception as e:
                logger.error("an exception hanpend in FPS thread , reason unkown!, e:")
                traceback.format_exc()
                G.device.get_pid()
        logger.debug("FPS stop event is set or timeout")


if __name__ == "__main__":
    from device import AndroidDevice

    G.device = AndroidDevice(serialno="emulator-5554", server_addr=["localhost", "5037"],
                             package="com.road7.ddtdmxandroid.ld", save_dir="localhost")
    G.device.start_app()
    mem = FPSMonitor("./FPS.txt")
    mem.start()
    time.sleep(300)
    mem.stop()
