import sys

sys.path.append("../")
import logging
import threading
from builtins import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__file__)


class GlobalData(object):
    suspend_event = threading.Event()  # 暂停,默认值是False，False是暂停，True是运行中
    stop_event = threading.Event()  # 停止，默认是False，False 是停止， True 是运行中
