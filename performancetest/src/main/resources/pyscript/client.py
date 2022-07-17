from ast import main
from asyncio import subprocess
from re import S
from sys import stdout
import requests
from threading import Thread

def start():
    res = requests.get("http://localhost:8080/start?pcId=1&host=10.130.131.79&port=5039&serial=e03c55d0&packageName=com.happyelements.AndroidAnimal")
    print(res.text)

def wsRead():
    f = Feed("ws://localhost:8080/send/1")
    f.start()

def stop():
    res = requests.get("http://localhost:8080/stop?pcId=1")
    print(res.text)


import json
import websocket    # pip install websocket-client

class Feed(object):

    def __init__(self, url):
        self.url = url      # 这里输入websocket的url
        self.ws = None

    def on_data(self, ws):
        pass

    def on_open(self, ws):
        """
         open connect and send pcid
        """
        print('A new WebSocketApp is opened!')

        # 开始订阅（举个例子）
        ws.send(1)

    def on_message(self, ws, message):
        """
        Callback object which is called when received data.
        2 arguments:
        @ ws: the WebSocketApp object
        @ message: utf-8 data received from the server
        """
        # 对收到的message进行解析
        print("收到", message)
        if "cmd:" in message:
            # cmds = message.split("cmd:")
            res = []
            def run(cmd, res):
                result = subprocess.run("1")
                res.append(result)
                print(result, "end")
            th = Thread(target=run, args=cmds[-1])
            th.start()
            # th.join()
            self.ws.send("1")

    def on_error(self, ws, error):
        """
        Callback object which is called when got an error.
        2 arguments:
        @ ws: the WebSocketApp object
        @ error: exception object
        """
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        """
        Callback object which is called when the connection is closed.
        2 arguments:
        @ ws: the WebSocketApp object
        @ close_status_code
        @ close_msg
        """
        print('The connection is closed!')

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_data=self.on_data,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()


if __name__ == "__main__":
    # print(start())
    wsRead()