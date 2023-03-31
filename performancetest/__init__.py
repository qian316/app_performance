# _*_ coding: utf-8 _*_
import time
from multiprocessing import Process
from threading import Thread


def c():
    def t():
        time.sleep(5)
        print(1)

    Thread(target=t).start()


if __name__ == '__main__':
    Process(target=c).start()
