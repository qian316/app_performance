# _*_ coding: utf-8 _*_
import sys

sys.path.append("../")
from builtins import *

from pydantic import BaseModel


class TaskEntity(BaseModel):
    serialno: str
    port: int
    package: str

class DeviceEntity(BaseModel):
    serialno: str
    
class PackageEntity(BaseModel):
    serialno: str
    package: str