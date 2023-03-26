import http.server
import platform
import subprocess
import sys
import time
import traceback
sib = "sib"
if sys.platform == "win32":
    sib = "Windows_x86_64\sib.exe"
elif sys.platform == "darwin":
    arch = platform.processor()
    if 'arm' in arch.lower():
        print("ARM Architecture")
        sib = "Mac_arm/sib"
    else:
        print("x86 Architecture")
        sib = "Mac_x86_64/sib"

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    sib_process = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/resetsib':
            self.reset_sib()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'SIB reset')
        elif self.path == '/stop':
            self.kill_sib()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'SIB stop')
        # else:
        #     super().do_GET()

    def reset_sib(self):
        try:
            self.kill_sib()
        except Exception as e:
            traceback.print_exc()
        try:
            self.start_sib()
        except Exception as e:
            traceback.print_exc()

    def start_sib(self):
        return_code = subprocess.run([sib, 'mount'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        msg = return_code.stdout.decode()
        # print("msg:", msg)
        if "mount successful!" in msg:
            print("ios sdk 启动成功")
        elif "no device connected" in msg:
            print("未连接手机, 请连接手机")
            time.sleep(3)
        else:
            print("发生异常,请重新连接手机, 重新启动sdk")
            time.sleep(3)
            exit()
        MyRequestHandler.sib_process = subprocess.Popen([sib, 'remote', 'share'], stderr=subprocess.PIPE,
                                                        stdout=subprocess.PIPE)
        print("new", MyRequestHandler.sib_process.pid)
        # outs, errs = MyRequestHandler.sib_process.communicate()
        # print(outs.decode())

    def kill_sib(self):
        if MyRequestHandler.sib_process:
            MyRequestHandler.sib_process.kill()
            time.sleep(1)
            print("sdk kill", MyRequestHandler.sib_process.pid)


if __name__ == '__main__':
    # 启动 SIB
    handler = MyRequestHandler
    handler.start_sib(handler)

    # 启动 HTTP 服务器
    httpd = http.server.HTTPServer(('0.0.0.0', 9130), MyRequestHandler)
    print('Server listening on localhost:9130')
    httpd.serve_forever()
