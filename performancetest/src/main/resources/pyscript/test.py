from ast import main
import requests

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

CHANNELS_WS = [
    # 这里输入需要订阅的频道
]


class Feed(object):

    def __init__(self, url):
        self.url = url      # 这里输入websocket的url
        self.ws = None

    def on_open(self, ws):
        """
        Callback object which is called at opening websocket.
        1 argument:
        @ ws: the WebSocketApp object
        """
        print('A new WebSocketApp is opened!')

        # 开始订阅（举个例子）
        sub_param = {"op": "subscribe", "args": CHANNELS_WS}
        sub_str = json.dumps(sub_param)
        ws.send(sub_str)
        print("Following Channels are subscribed!")
        print(CHANNELS_WS)

    def on_data(self, ws, string, type, continue_flag):
        """
        4 argument.
        The 1st argument is this class object.
        The 2nd argument is utf-8 string which we get from the server.
        The 3rd argument is data type. ABNF.OPCODE_TEXT or ABNF.OPCODE_BINARY will be came.
        The 4th argument is continue flag. If 0, the data continue
        """

    def on_message(self, ws, message):
        """
        Callback object which is called when received data.
        2 arguments:
        @ ws: the WebSocketApp object
        @ message: utf-8 data received from the server
        """
        # 对收到的message进行解析
        print(message)

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
    print(start())
    wsRead()