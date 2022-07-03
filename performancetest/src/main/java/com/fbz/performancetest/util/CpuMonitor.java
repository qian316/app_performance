package com.fbz.performancetest.util;


import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

public class CpuMonitor extends Monitor {

    private final Device device;

    private final String packageName;
    private final ProcessUtil processUtil = new ProcessUtil();
    private String pid;
    private ArrayList<Map<String, String>> cpuResult = new ArrayList<>();

    private boolean isRun = false;

    public CpuMonitor(Device device, String packageName) {
        this.device = device;
        this.packageName = packageName;
    }

    public String getCpu() {
        return processUtil.getBack(device.adbShell(String.format("top -n 1 -p %s", pid) + " -o %CPU -b -q"));
    }

    public void realGetCpuInfo() {
        System.out.println("join");
        pid = device.getPid(packageName);
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        while (isRun) {
            String cpuItemInfo = getCpu();
            if (cpuItemInfo == null || "".equals(cpuItemInfo)) {
                pid = device.getPid(packageName);
                if (pid == null || "".equals(pid)) {
                    throw new RuntimeException("未启动app");
                }
            }
            Map<String, String> itemResultMap = new HashMap<>();
            itemResultMap.put("time", dateFormat.format(new Date()));
            itemResultMap.put("cpu", cpuItemInfo);
            cpuResult.add(itemResultMap);
            System.out.println(cpuResult);
        }

    }

    @Override
    public boolean start() {
        isRun = true;
        Thread thread = new Thread(() -> {
            realGetCpuInfo();
        });
        thread.start();
        return true;
    }


    @Override
    public boolean stop() {
        isRun = false;
        return true;
    }

    public static void main(String[] args) throws InterruptedException {
        Device device = new Device("10.130.131.79", 5039, "e03c55d0");
        String apk = "com.happyelements.AndroidAnimal";
        device.startApk(apk);
        if(device.apkIsStart(apk)){
            CpuMonitor cpuMonitor = new CpuMonitor(device, apk);
            cpuMonitor.start();
            Thread.sleep(10000);
            cpuMonitor.stop();
        }
    }
}
