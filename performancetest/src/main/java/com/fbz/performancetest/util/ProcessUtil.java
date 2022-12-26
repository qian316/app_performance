package com.fbz.performancetest.util;

import com.fbz.performancetest.PerformancetestApplication;
import com.fbz.performancetest.config.ConnectException;
import lombok.extern.slf4j.Slf4j;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
@Slf4j
public class ProcessUtil {

    private Process process = null;

    public String exec(String cmd) throws IOException {
        try{
            String [] commandCmds = cmd.split(" ");
            ProcessBuilder processBuilder = new ProcessBuilder().command(commandCmds);
            processBuilder.redirectErrorStream(true);
            process = processBuilder.start();
            byte [] bytes = process.getInputStream().readAllBytes();
            return new String(bytes);
        }catch (Exception e){
            throw e;
        }finally {
            if (process.isAlive()) {
                process.destroy();
            }
        }
    }

    public static void main(String[] args) {
        ProcessUtil p = new ProcessUtil();
        String res = p.getBack("adb -H 10.130.131.79 -P 5039 -s e03c55d0 shell top -n 1 -p 7188 -o %CPU -b -q", "1");
        System.out.println(res);
    }

    //core exec shell
    public String getBack(String cmd, String pcId) {
   /*     if (pcId != null && PerformancetestApplication.webSocketMap.getOrDefault(pcId, null) != null){
            synchronized (ProcessUtil.class){
                int beforesend = PerformancetestApplication.webSocketMap.get(pcId).clientMessage.size();
                PerformancetestApplication.webSocketMap.get(pcId).sendMessage("cmd:" + cmd);
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                if(PerformancetestApplication.webSocketMap.get(pcId).clientMessage.size() - 1 == beforesend){
                    return PerformancetestApplication.webSocketMap.get(pcId).clientMessage.get(beforesend);
                }
                throw new ConnectException("执行失败");
            }
        }*/
        try {
            return this.exec(cmd);
        } catch (IOException e) {
            e.printStackTrace();
            log.error(String.format("执行失败 %s", cmd));
        }
        return null;
    }
}
