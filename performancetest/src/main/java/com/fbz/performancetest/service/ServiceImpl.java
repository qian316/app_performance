package com.fbz.performancetest.service;

import com.fbz.performancetest.PerformancetestApplication;
import com.fbz.performancetest.util.CpuMonitor;
import com.fbz.performancetest.util.Device;
import com.fbz.performancetest.util.MemoryMonitor;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@org.springframework.stereotype.Service
public class ServiceImpl implements Service {

    @Override
    public String start(String pcId, String host, Integer port, String serial, String packageName) {
        Device device = new Device(host, port, serial);
        String apk = packageName;
        device.startApk(apk);
        if (device.apkIsStart(apk)) {
            CpuMonitor cpuMonitor = new CpuMonitor(device, apk);
            MemoryMonitor memoryMonitor = new MemoryMonitor(device, apk);
            cpuMonitor.start();
            memoryMonitor.start();
            PerformancetestApplication.objectMap.put(pcId + "cpu", cpuMonitor);
            PerformancetestApplication.objectMap.put(pcId + "memory", memoryMonitor);
        }
        return pcId;
    }

    @Override
    public boolean stop(String pcId) {
        Object cpuMonitor = PerformancetestApplication.objectMap.get(pcId + "cpu");
        Object memoryMonitor = PerformancetestApplication.objectMap.get(pcId + "memory");
        if (cpuMonitor != null) {
            ((CpuMonitor) cpuMonitor).stop();
        }
        if (memoryMonitor != null) {
            ((MemoryMonitor) memoryMonitor).stop();
        }
        PerformancetestApplication.objectMap.remove(pcId + "cpu", cpuMonitor);
        PerformancetestApplication.objectMap.remove(pcId + "memory", memoryMonitor);
        return true;
    }

    @Override
    public Map<String, List> getAllInfo(String pcId) {
        HashMap<String, List> res = new HashMap<>();
        res.put("cpu", ((CpuMonitor) PerformancetestApplication.objectMap.get(pcId + "cpu")).getCpuResult());
        res.put("memory", ((MemoryMonitor) PerformancetestApplication.objectMap.get(pcId + "memory")).getMemoryResult());
        return res;
    }
}
