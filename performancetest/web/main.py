# _*_ coding: utf-8 _*_
import collections
import datetime
import os
import time
from builtins import *
from threading import Thread

from airtest.core.android.adb import ADB
from fastapi import FastAPI, Request
from func_timeout import func_set_timeout, FunctionTimedOut

from core.global_data import logger
from core.task_handle import TaskHandle
from web.dao import connect, Task
from web.entity import TaskEntity

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
    package = task.package
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
        new_task = Task(host=client_host, port=port, serialno=serialno, start_time=datetime.datetime.now(), status=status, file_dir=file_dir, package=package)
        session.add(new_task)
        session.commit()
        run_all_monitor(serialno, [client_host, port], package, file_dir)
        # new_task.pid = pid
        # new_task.status = 1
        # session.commit()
    return {"code": 200}


def run_all_monitor(serialno, server_addr: list, package, save_dir):
    task_process = TaskHandle(serialno=serialno, server_addr=server_addr, package=package, save_dir=save_dir)
    task_process.start()


@func_set_timeout(5)
def adb_devices(adb):
    return adb.devices()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
