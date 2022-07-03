package com.fbz.performancetest.util;

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
        String res = p.getBack("adb -H 10.130.131.79 -P 5039 -s e03c55d0 shell top -n 1 -p 7188 -o %CPU -b -q");
        System.out.println(res);
    }

    public void write(String cmd) throws IOException {
        OutputStream outputStream = process.getOutputStream();
        outputStream.write(cmd.getBytes());
    }

    public String getBack(String cmd){
        try {
            this.exec(cmd);
        } catch (IOException e) {
            e.printStackTrace();
            throw new RuntimeException("执行失败");
        }
        try {
            return this.read();
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            throw new RuntimeException("读取失败");
        }
    }

    public String read() throws IOException, InterruptedException {
        byte[] bytes = process.getInputStream().readAllBytes();
        if (bytes.length != 0) {
            return new String(bytes);
        }
        throw new RuntimeException(new String(process.getErrorStream().readAllBytes()));
    }
}
