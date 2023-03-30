# _*_ coding: utf-8 _*_
from builtins import *

from pydantic import BaseModel


class TaskEntity(BaseModel):
    serialno: str
    port: int
    package: str
