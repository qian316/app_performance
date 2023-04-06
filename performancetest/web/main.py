# _*_ coding: utf-8 _*_
import datetime
import os
import platform
import re
import sys
import time
import traceback
from builtins import *

import psutil
from airtest.core.android.adb import ADB
from fastapi import FastAPI, Request
from func_timeout import func_set_timeout, FunctionTimedOut
from starlette.responses import RedirectResponse, JSONResponse
from starlette.staticfiles import StaticFiles

sys.path.append("../")
from performancetest.core.global_data import logger
from performancetest.core.task_handle import TaskHandle
from performancetest.web.dao import connect, Task
from performancetest.web.entity import DeviceEntity, PackageEntity, TaskEntity
from performancetest.web.util import DataCollect

app = FastAPI()
BASE_CSV_DIR = os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], "test_result")
BASE_SDK_DIR = os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], "sdk")
app.mount("/static", StaticFiles(directory=BASE_CSV_DIR), name="static")
app.mount("/sdk", StaticFiles(directory=BASE_SDK_DIR), name="sdk")


# 定义异常处理程序
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={"code": "500", "err": exc.args},
    )


# 中间件函数
@app.middleware("http")
async def handle_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except BaseException as exc:
        return await exception_handler(request, exc)


@app.get("/")
async def index():
    return RedirectResponse(url="/static/index.html")


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


@app.post("/get_local_device_packages/")
async def get_local_device_packages(request: Request, device: DeviceEntity):
    client_host: str = request.client.host
    try:
        adb: ADB = ADB(server_addr=(client_host, 5037), serialno=device.serialno)
        app_list: list = adb_app_list(adb)
    except FunctionTimedOut as e:
        return []
    logger.info(app_list)
    return app_list


@app.post("/get_local_device_packages_version/")
async def get_local_device_packages_version(request: Request, package: PackageEntity):
    client_host: str = request.client.host
    adb: ADB = ADB(server_addr=(client_host, 5037), serialno=package.serialno)
    package_info = adb.shell(['dumpsys', 'package', package.package])
    matcher = re.search(r'versionName=(.*)', package_info)
    if matcher:
        version = matcher.group(1)
    else:
        version = ''
    return version


@app.get("/get_all_task/")
async def get_all_task(request: Request):
    client_host: str = request.client.host
    with connect() as session:
        all_task = session.query(Task).filter(Task.host == client_host).filter(Task.id != 1).all()
        logger.info(all_task)
        res: list = [i.to_dict() for i in all_task]
        res.reverse()
        try:
            if res and res[0].get("status") == 1:
                res.insert(1, session.query(Task).filter(Task.id == 1).first().to_dict())
            else:
                res.insert(0, session.query(Task).filter(Task.id == 1).first().to_dict())
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
        return res


@app.post("/run_task/")
async def run_task(request: Request, task: TaskEntity):
    client_host: str = request.client.host
    port = task.port
    serialno = task.serialno
    package = task.package
    start_time = time.time()
    status = 0
    file_dir = os.path.join(BASE_CSV_DIR, client_host, str(int(start_time)))
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    return_task_id = None
    with connect() as session:
        task_running_count = session.query(Task).filter(Task.host == client_host).filter(Task.port == port).filter(
            Task.status != 2).count()
        if task_running_count > 0:
            raise Exception("当然仍有任务在进行无法创建新任务")
        new_task = Task(host=client_host, port=port, serialno=serialno, start_time=datetime.datetime.now(),
                        status=status, file_dir=file_dir, package=package)
        session.add(new_task)
        run_all_monitor(serialno, [client_host, port], package, file_dir)
        return_task_id = new_task.id
    return {"code": 200, "taskid": return_task_id}


def run_all_monitor(serialno, server_addr: list, package, save_dir):
    task_process = TaskHandle(serialno=serialno, server_addr=server_addr, package=package, save_dir=save_dir)
    task_process.start()


@app.get("/stop_task/")
async def stop_task(request: Request, id: int):
    client_host: str = request.client.host
    with connect() as session:
        task_item = session.query(Task).filter(Task.id == id).filter(Task.host == client_host).first()
        try:
            proc = psutil.Process(task_item.pid)
            proc.kill()
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
        task_item.status = 2
        task_item.end_time = datetime.datetime.now()
    return {"code": 200}


@app.get("/get_task_status/")
async def get_task_status(request: Request, id: int):
    client_host: str = request.client.host
    with connect() as session:
        task_item = session.query(Task).filter(Task.id == id).filter(Task.host == client_host).first()
        return task_item.to_dict()


@app.get("/result/")
async def result(request: Request, id: int):
    client_host: str = request.client.host
    with connect() as session:
        if int(id) == 1:
            task_item = session.query(Task).filter(Task.id == id).first()
            if "Windows" in platform.platform():
                task_item.file_dir = task_item.file_dir.replace("/", "\\")
                _, relative_path = task_item.file_dir.split("test_result\\")
            else:
                task_item.file_dir = task_item.file_dir.replace("\\", "/")
                _, relative_path = task_item.file_dir.split("test_result/")
            parent = os.path.dirname(os.path.abspath(__file__))
            base, _ = os.path.split(parent)
            task_item.file_dir = os.path.join(base, "test_result", relative_path)
        else:
            task_item = session.query(Task).filter(Task.id == id).filter(Task.host == client_host).first()
        try:
            result = DataCollect.read_data_all(task_item.file_dir)
        except BaseException as e:
            logger.error(e)
            traceback.print_exc()
            return {"result": {}}
        return {"result": result}


@func_set_timeout(5)
def adb_devices(adb):
    return adb.devices()


@func_set_timeout(5)
def adb_app_list(adb):
    return adb.list_app(third_only=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
