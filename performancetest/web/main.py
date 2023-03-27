# _*_ coding: utf-8 _*_
import collections
import os
import time
from builtins import *

from airtest.core.android.adb import ADB
from fastapi import FastAPI, Request
from func_timeout import func_set_timeout, FunctionTimedOut

from performancetest.core.global_data import logger
from performancetest.core.task_handle import TaskHandle
from performancetest.web.dao import connect, Task
from performancetest.web.entity import TaskEntity

app = FastAPI()
app.state.monitor_dict = collections.OrderedDict
BASE_CSV_DIR = os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], "test_result")


@app.get("/get_local_device/")
async def create_item(request: Request):
    client_host: str = request.client.host
    try:
        adb: ADB = ADB(server_addr=(client_host, 5037))
        devices: list = adb_devices(adb)
    except FunctionTimedOut as e:
        return []
    res_list: list = []
    for i in devices:
        adb.serialno = i[0]
        info: dict = adb.get_device_info()
        info["host"] = client_host
        info["port"] = 5037
        res_list.append(info)

    logger.info(res_list)
    return res_list


@app.post("/run_task/")
async def run_task(request: Request, task: TaskEntity):
    client_host: str = request.client.host
    port = task.port
    serialno = task.serialno
    start_time = time.time()
    status = 0
    file_dir = os.path.join(BASE_CSV_DIR, str(int(start_time)))
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    with connect() as session:
        task_running_count = session.query(Task).filter(Task.host == client_host).filter(Task.port == port).filter(
            Task.status != 2).count()
        if task_running_count > 0:
            raise Exception("当然仍有任务在进行无法创建新任务")
        new_task = Task(host=client_host, port=port, serialno=serialno, start_time=start_time, status=status,
                        file_dir=file_dir)
        session.add(new_task)
        pid = run_all_monitor()



def run_all_monitor():
    task_process = TaskHandle(serialno="emulator-5554", server_addr=["localhost", "5037"],
               package="com.road7.ddtdmxandroid.ld", save_dir="localhost")
    task_process.start()
    return task_process.pid
    # G.device = AndroidDevice()
    # G.logcat = Logcat(package="com.road7.ddtdmxandroid.ld", save_dir="../core/")
    # time.sleep(1)
    # G.device.start_app()
    # CpuMonitor("./cpu.txt").start()
    # MemoryMonitor("./memory.txt").start()
    # FPSMonitor("./FPS.txt").start()
    # GpuMonitor("./gpu.txt").start()
    # DeviceBatteryMonitor("./deviceBattery.txt").start()


@func_set_timeout(5)
def adb_devices(adb):
    return adb.devices()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)