package com.fbz.performancetest.service;

import com.fbz.performancetest.PerformancetestApplication;
import com.fbz.performancetest.util.*;

import java.util.HashMap;
import java.util.List;

@org.springframework.stereotype.Service
public class ServiceImpl implements Service {

    @Override
    public ResultBean<Boolean> connect(String pcId, String host, Integer port, String serial) {
        Device device = new Device(host, port, serial, pcId);
        return device.connectDevices();
    }

    @Override
    public ResultBean<String []> getAllPackage(String pcId, String host, Integer port, String serial) {
        Device device = new Device(host, port, serial, pcId);
        return device.getAllPackage();
    }

    @Override
    public ResultBean<String> start(String pcId, String host, Integer port, String serial, String packageName) {
        Device device = new Device(host, port, serial, pcId);
        String apk = packageName;
        device.startApk(apk);
        if (device.apkIsStart(apk)) {
            CpuMonitor cpuMonitor = new CpuMonitor(device, apk);
            MemoryMonitor memoryMonitor = new MemoryMonitor(device, apk);
            cpuMonitor.start();
            memoryMonitor.start();
        }
        return ResultBeanUtil.success(pcId);
    }

    @Override
    public ResultBean<Boolean> stop(String pcId) {
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
        return ResultBeanUtil.success(true);
    }

    @Override
    public ResultBean<HashMap<String, List>> getAllInfo(String pcId) {
        HashMap<String, List> res = new HashMap<>();
        res.put("cpu", ((CpuMonitor) PerformancetestApplication.objectMap.get(pcId + "cpu")).getCpuResult());
        res.put("memory", ((MemoryMonitor) PerformancetestApplication.objectMap.get(pcId + "memory")).getMemoryResult());
        return ResultBeanUtil.success(res);
    }
}
