import asyncio
import subprocess

import websockets

# 向服务器端发送认证后的消息
async def send_msg(websocket):
    while True:
        _text = None
        if _text == "exit":
            print(f'you have enter "exit", goodbye')
            await websocket.close(reason="user exit")
            return False
        if _text:
            await websocket.send(_text)
        recv_text = await websocket.recv()
        print(f"{recv_text}")
        res = subprocess.run(recv_text.split("cmd:")[-1])
        _text = res
# 客户端主逻辑
async def main_logic():
    async with websockets.connect('ws://localhost:8080/send/1') as websocket:
        await send_msg(websocket)

asyncio.get_event_loop().run_until_complete(main_logic())