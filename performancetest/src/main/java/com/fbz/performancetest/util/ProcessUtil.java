package com.fbz.performancetest.util;

import com.fbz.performancetest.PerformancetestApplication;
import com.fbz.performancetest.config.ConnectException;

import java.io.IOException;
import java.io.OutputStream;

public class ProcessUtil {

    private Process process = null;

    public Process exec(String cmd) throws IOException {
        process = Runtime.getRuntime().exec(cmd);
        return process;
    }

    public static void main(String[] args) {
        ProcessUtil p = new ProcessUtil();
        String res = p.getBack("adb -H 10.130.131.79 -P 5039 -s e03c55d0 shell top -n 1 -p 7188 -o %CPU -b -q", "1");
        System.out.println(res);
    }

    public void write(String cmd) throws IOException {
        OutputStream outputStream = process.getOutputStream();
        outputStream.write(cmd.getBytes());
    }

    public String getBack(String cmd, String pcId) {
        if (pcId != null && PerformancetestApplication.webSocketMap.getOrDefault(pcId, null) != null){
            synchronized (ProcessUtil.class){
                int beforesend = PerformancetestApplication.webSocketMap.get(pcId).clientMessage.size();
                PerformancetestApplication.webSocketMap.get(pcId).sendMessage("cmd:" + cmd);
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                if(PerformancetestApplication.webSocketMap.get(pcId).clientMessage.size() - 1 == beforesend){
                    return PerformancetestApplication.webSocketMap.get(pcId).clientMessage.get(beforesend + 1);
                }
                throw new ConnectException("执行失败");
            }
        }
        try {
            this.exec(cmd);
        } catch (IOException e) {
            e.printStackTrace();
            throw new ConnectException("执行失败");
        }
        try {
            return this.read();
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            throw new ConnectException("读取失败");
        }
    }

    public String read() throws IOException, InterruptedException {
        byte[] bytes = process.getInputStream().readAllBytes();
        if (bytes.length != 0) {
            return new String(bytes);
        }
        throw new ConnectException(new String(process.getErrorStream().readAllBytes()));
    }
}
