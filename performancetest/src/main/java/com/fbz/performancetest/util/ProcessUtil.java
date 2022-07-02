package com.fbz.performancetest.util;

import java.io.IOException;
import java.io.OutputStream;

public class ProcessUtil {

    private Process process = null;

    public Process exec(String cmd) throws IOException {
        process = Runtime.getRuntime().exec(cmd);
        return process;
    }

    public String read() throws IOException {
        byte [] bytes = process.getInputStream().readAllBytes();
        return new String(bytes);
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
        } catch (IOException e) {
            e.printStackTrace();
            throw new RuntimeException("读取失败");
        }
    }

    public static void main(String[] args) {

    }
}
