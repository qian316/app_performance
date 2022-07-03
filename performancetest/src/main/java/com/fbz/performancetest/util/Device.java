package com.fbz.performancetest.util;

import java.io.File;
import java.util.Arrays;

public class Device {
    private String host = "localhost";
    private Integer port = 5037;
    private String serial = null;
    private ProcessUtil processUtil = new ProcessUtil();
    private String adb = System.getProperty("user.dir") + File.separator + "adbtools" + File.separator + (System.getProperty("os.name").toLowerCase().contains("win") ? "Windows" + File.separator + "adb.exe" : System.getProperty("os.name").toLowerCase().contains("linux") ? "Linux" + File.separator + "adb" : "Darwin" + File.separator + "adb" );
    public void startApk(String packageName) {
        String act = processUtil.getBack(adbShell(String.format("monkey -p  %s -c android.intent.category.LAUNCHER 1", packageName)));
    }

    public String adbShell(String keyWords) {
        if (serial == null) {
            throw new RuntimeException("not device");
        }
        return String.format(adb + " -H %s -P %s -s %s shell %s", host, port, serial, keyWords);
    }

    public boolean apkIsStart(String packageName) {
        String res = processUtil.getBack(adbShell(String.format(("dumpsys window | grep %s"), packageName)));
        System.out.println("device is start:" + res);
        res = res.replace(" ", "");
        if (res != null && !"".equals(res)) {
            return true;
        }
        return false;
    }

    public String getPid(String packageName) {
        String res = processUtil.getBack(adbShell(String.format(("ps | grep  %s"), packageName)));
        String [] info = res.split(" ");
        info = Arrays.stream(info).filter(x -> !"".equals(x)).toArray(String[]::new);
        System.out.println(Arrays.toString(info));
        String pidNumber = info[1];
        System.out.println("pidinfo is" + res);
        System.out.println("pid is " + pidNumber);
        return pidNumber;
    }


    public Device(String serial) {
        this.serial = serial;
    }

    public Device(Integer port, String serial) {
        this.port = port;
        this.serial = serial;
    }

    public Device(String host, Integer port, String serial) {
        this.host = host;
        this.port = port;
        this.serial = serial;
    }

    public String getHost() {
        return host;
    }

    public void setHost(String host) {
        this.host = host;
    }

    public Integer getPort() {
        return port;
    }

    public void setPort(Integer port) {
        this.port = port;
    }

    public String getSerial() {
        return serial;
    }

    public void setSerial(String serial) {
        this.serial = serial;
    }

    public String getAllApk() {
        return processUtil.getBack(adbShell("pm list package"));
    }

    public static void main(String[] args) {
        Device device = new Device("10.130.131.79", 5039, "e03c55d0");
        String res = device.getAllApk();
        System.out.println(res);
        device.startApk("com.happyelements.AndroidAnimal");
        System.out.println(device.apkIsStart("com.happyelements.AndroidAnimal"));

    }
}
