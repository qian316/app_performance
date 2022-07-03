package com.fbz.performancetest.controller;

import com.fbz.performancetest.service.Service;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@RestController
public class AllController {

    @Resource
    Service service;

    @RequestMapping("/start")
    public String startTask(String pcId, String host, Integer port, String serial, String packageName) {
        return service.start(pcId, host, port, serial, packageName);
    }

    @RequestMapping("/getAllInfo")
    public Map<String, List> getAllInfo(String pcId) {
        return service.getAllInfo(pcId);
    }

    @RequestMapping("/stop")
    public boolean stopTask(String pcId) {
        return service.stop(pcId);
    }
}
