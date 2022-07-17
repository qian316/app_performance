package com.fbz.performancetest.util;


import java.text.SimpleDateFormat;
import java.util.*;

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
        return processUtil.getBack(device.adbShell(String.format("top -n 1 -p %s", pid) + " -o %CPU -b -q"), this.device.pcId);
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
//            System.out.println(cpuResult);
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


    public List<Object[]> getCpuResult() {
        List<Object[]> resList = new ArrayList<>();
        Map<String, String> itemResultMap = new HashMap<>();
        itemResultMap.put("time", "end");
        itemResultMap.put("cpu", "end");
        cpuResult.add(itemResultMap);
        int left = 0;
        int right = 0;
        double valueSum = 0;
        while (right < cpuResult.size()) {
            String time = cpuResult.get(left).get("time");
            if ("end".equals(time)) {
                cpuResult.remove(itemResultMap);
                break;
            }
            if(time.equals(cpuResult.get(right).get("time"))){
                valueSum += Double.valueOf(cpuResult.get(right).get("cpu"));
                right++;
            }else {
                Object[] tmp = new Object[2];
                tmp[0] = time;
                tmp[1] = valueSum / (right - left);
                resList.add(tmp);
                left = right;
                valueSum = 0;
            }
        }
        return resList;
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
            System.out.println("res: "+cpuMonitor.getCpuResult());
        }
//        Map<String, String> itemResultMap = new HashMap<>();
//        itemResultMap.put("time", "11");
//        itemResultMap.put("cpu", "20");
//        Map<String, String> itemResultMap1 = new HashMap<>();
//        itemResultMap1.put("time", "11");
//        itemResultMap1.put("cpu", "22");
//        Map<String, String> itemResultMap2 = new HashMap<>();
//        itemResultMap2.put("time", "11");
//        itemResultMap2.put("cpu", "23");
//        Map<String, String> itemResultMap3 = new HashMap<>();
//        itemResultMap3.put("time", "13");
//        itemResultMap3.put("cpu", "13");
//        cpuMonitor.cpuResult.add(itemResultMap);
//        cpuMonitor.cpuResult.add(itemResultMap1);
//        cpuMonitor.cpuResult.add(itemResultMap2);
//        cpuMonitor.cpuResult.add(itemResultMap3);
//        System.out.println(cpuMonitor.getCpuResult());
    }
}
