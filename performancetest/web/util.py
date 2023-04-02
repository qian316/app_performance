import sys
sys.path.append("../")
import concurrent.futures
import os
from builtins import *

import numpy as np

from performancetest.core.global_data import logger


class DataCollect(object):

    def __init__(self, file_dir_path=None):
        """
        任务所在文件夹, 设置了这个文件夹其他的不需要再传file_path
        """
        self.file_dir_path = file_dir_path
        self.is_need_relative_time = False

    def __read_csv_file(self, file_path=None, skip_rows=1, usecols=None):
        """
        读取cpu，memory，fps，gpu，温度等csv文件的值
        """
        if not usecols:
            # csv_data = np.loadtxt(file_path, skiprows=skip_rows, delimiter=",", dtype=float)
            csv_data = np.genfromtxt(file_path, skip_header=skip_rows, delimiter=",", dtype=float, filling_values=0)
        else:
            # csv_data = np.loadtxt(file_path, skiprows=skip_rows, delimiter=",", dtype=float, usecols=usecols)
            csv_data = np.genfromtxt(file_path, skip_header=skip_rows, delimiter=",", dtype=float, filling_values=0,
                                     usecols=usecols)
        return csv_data

    def __read_cpu(self, file_path=None):
        if not file_path:
            file_path = os.path.join(self.file_dir_path, "cpu.csv")
        return self.__read_csv_file(file_path=file_path)

    def __read_memory(self, file_path=None):
        if not file_path:
            file_path = os.path.join(self.file_dir_path, "memory.csv")
        return self.__read_csv_file(file_path=file_path)

    def __read_gpu(self, file_path=None):
        if not file_path:
            file_path = os.path.join(self.file_dir_path, "gpu.csv")
        return self.__read_csv_file(file_path=file_path)

    def __read_device_temperature(self, file_path=None):
        if not file_path:
            file_path = os.path.join(self.file_dir_path, "devicebattery.csv")
        return self.__read_csv_file(file_path=file_path, usecols=(0, 1))

    def __read_device_battery_level(self, file_path=None):
        if not file_path:
            file_path = os.path.join(self.file_dir_path, "devicebattery.csv")
        return self.__read_csv_file(file_path=file_path, usecols=(0, 2))

    def __read_fps(self, file_path=None):
        if not file_path:
            file_path = os.path.join(self.file_dir_path, "fps.csv")
        return self.__read_csv_file(file_path=file_path)

    # 监控类型对应的读取方法
    __monitortype_func = {"cpu": __read_cpu, "memory": __read_memory, "fps": __read_fps,
                          "gpu": __read_gpu, "devicebatterytemperature": __read_device_temperature,
                          "devicebatterylevel": __read_device_battery_level}

    # 读数据的方法使用：DataCollect.read_data(1, "cpu", "memory", "fps")
    @classmethod
    def read_data(cls, file_dir_path: int, /, *args, **kwargs):
        """
        param: "cpu", "memory"
        return:
        {
            public_imgs：[{"16xxxxxx": "pic_path"}, {"16xxxxxx": "pic_path1"}]
            public_start_time：16xxxxxx: int,
            public_end_time：16xxxxxx: int,
            cpu: {
                 time：[16xxxxxx, 16xxxxxx]  //cpu,memory,fps 开始真实时间戳相同
                 value: [100, 101]
                 relative_time: [00:00, 00:10]
            },
            memory: {
                  time：[16xxxxxx, 16xxxxxx]  //cpu,memory,fps 开始真实时间戳相同
                 value: [100, 101]

            }
        }
        """
        return cls.item_subtask_result(file_dir_path, monitortypes=args,
                                       is_need_relative_time=kwargs.get("is_need_relative_time", True))

    # 读所有类型的数据的方法使用：DataCollect.read_data(1, "cpu", "memory", "fps")
    @classmethod
    def read_data_all(cls, file_dir_path):
        return cls.read_data(file_dir_path, *cls.__monitortype_func.keys())

    @classmethod
    def item_subtask_result(cls, file_dir_path: int, monitortypes: tuple, **kwargs):
        data_collect = DataCollect(file_dir_path=file_dir_path)
        item_subtask_result_dict: dict = {}  # 存储每种监控类型的结果
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 执行所有读取
            wait_task: list = []
            for monitor_name in monitortypes:
                future = executor.submit(cls.__monitortype_func.get(monitor_name), data_collect)
                item_subtask_result_dict[monitor_name] = future
                wait_task.append(future)
            # wait task end
            done, not_done = concurrent.futures.wait(wait_task, return_when=concurrent.futures.ALL_COMPLETED)
            for key, value_future in list(item_subtask_result_dict.items()):
                try:
                    value_future_res = value_future.result()
                    if value_future_res.ndim < 2:
                        raise Exception("数组低于2维度")
                    if len(value_future_res) <= 0:
                        raise Exception("数据结果为空")
                    item_subtask_result_dict[key] = value_future_res
                    # 如果是fps 会去掉第一个和 最后一个点
                    if key == "fps":
                        item_subtask_result_dict[key] = item_subtask_result_dict[key][1: -1] if len(
                            item_subtask_result_dict[key]) > 3 else item_subtask_result_dict[key]
                except Exception as e:
                    logger.error(e)
                    item_subtask_result_dict.pop(key, None)

            # 处理公共开始时间, 结束时间
            # logger.info("item{0}".format(item_subtask_result_dict))
            if item_subtask_result_dict:
                public_start_time, public_end_time = cls.get_public_time(item_subtask_result_dict)
                # 获取所有结果
                for (monitor_name, future_result) in item_subtask_result_dict.items():
                    item_subtask_result_dict[monitor_name] = cls.time_value_result(monitor_name, future_result,
                                                                                   public_start_time, public_end_time,
                                                                                   is_need_relative_time=kwargs.get(
                                                                                       "is_need_relative_time", False))
                item_subtask_result_dict["public_start_time"] = public_start_time
                item_subtask_result_dict["public_end_time"] = public_end_time
                img_path_dir = os.path.join(file_dir_path, "picture_log")
                if os.path.exists(img_path_dir):
                    task_dir, task_name_int = os.path.split(file_dir_path)
                    _, host = os.path.split(task_dir)
                    item_subtask_result_dict["public_imgs"] = cls.get_public_imgs(img_path_dir, public_start_time,
                                                                                  public_end_time, task_name_int, host)
        return item_subtask_result_dict

    @staticmethod
    def get_public_imgs(img_path_dir: str, public_start_time: int, public_end_time: int, task_name_int:str, host:str):
        all_imgs = os.listdir(img_path_dir)
        img_time_dict = {i: "" for i in range(public_start_time, public_end_time + 1)}
        for img in all_imgs:
            try:
                img_time_dict[int(int(
                    img.replace(".jpg", "")) * 0.001)] = "/static/{0}/{1}/picture_log/{2}".format(host, task_name_int, img)
            except Exception as e:
                logger.error(e)
        res_list = []
        for key, v in img_time_dict.items():
            try:
                res_list.append({"time": key, "picture_path": v,
                                 "relative_time": DataCollect.seconds_to_time(int(key) - public_start_time)})
            except Exception as e:
                logger.error(e)
        res_list.sort(key=lambda x: int(x.get("time")))
        return res_list

    @staticmethod
    def get_public_time(item_subtask_result_dict: dict):
        time_collect: list[list] = [list(map(lambda x: int(x), future_result[:, 0])) for monitor_name, future_result in
                                    item_subtask_result_dict.items()]  # 所有的时间[[], []]
        public_start_time, public_end_time = DataCollect.find_common_elements(time_collect)
        return public_start_time, public_end_time

    @staticmethod
    def find_common_elements(lists):
        # 找到所有列表的共同元素
        common_elements = set(lists[0])
        for i in range(1, len(lists)):
            common_elements &= set(lists[i])

        # 找到所有列表的共同元素中第一个和最后一个出现的值
        first_common_element = None
        last_common_element = None
        for element in lists[0]:
            if element in common_elements:
                first_common_element = element
                break
        for element in reversed(lists[0]):
            if element in common_elements:
                last_common_element = element
                break

        return first_common_element, last_common_element

    # 获取不同类型的数据，掐头去尾保证所有的数据起点终点一致
    @staticmethod
    def time_value_result(monitor_name, csv_data, start_time, end_time, **kwargs):
        real_time: list = csv_data[:, 0].tolist()
        value: list = np.round(csv_data[:, 1], 2).tolist()
        real_time_int: list = list(map(lambda x: int(x), real_time))
        start_index = real_time_int.index(start_time)
        end_index = real_time_int.index(end_time) + 1
        res_dict = {"time": real_time[start_index: end_index], "value": value[start_index: end_index]}
        if kwargs.get("is_need_relative_time", False):
            res_dict["relative_time"] = [DataCollect.seconds_to_time(item - start_time) for item in
                                         real_time_int[start_index: end_index]]
        if monitor_name == "fps":
            try:
                res_dict["full_number"] = max(csv_data[:, 3][start_index: end_index])
                res_dict["jank_number"] = csv_data[:, 4].tolist()[start_index: end_index]
                res_dict["big_jank_number"] = csv_data[:, 5].tolist()[start_index: end_index]
                res_dict["ftimege100"] = csv_data[:, 6].tolist()[start_index: end_index]
            except IndexError as e:
                res_dict["full_number"] = 0
                res_dict["jank_number"] = []
                res_dict["big_jank_number"] = []
                res_dict["ftimege100"] = []
                logger.error(e)
            # fps值需要去掉开头一个和最后一个
            res_dict["time"] = res_dict["time"][1: -2] if res_dict.get("time") else []
            res_dict["value"] = res_dict["value"][1: -2] if res_dict.get("value") else []
        return res_dict

    @staticmethod
    def seconds_to_time(time_data_collect):
        minutes = str(time_data_collect // 60).zfill(2)
        seconds = str(time_data_collect % 60).zfill(2)
        return f"{minutes}:{seconds}"


if __name__ == '__main__':
    d = DataCollect.read_data_all(r"C:\workproject\app_performance\performancetest\test_result\1680241056")
    # print(dir(d))
    print(d)
