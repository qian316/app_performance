package com.fbz.performancetest.controller;

import com.fbz.performancetest.service.Service;
import com.fbz.performancetest.util.ResultBean;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import java.util.HashMap;
import java.util.List;

@RestController
public class AllController {

    @Resource
    Service service;

    @RequestMapping("/start")
    public ResultBean<String> startTask(String pcId, String host, Integer port, String serial, String packageName) {
        return service.start(pcId, host, port, serial, packageName);
    }

    @RequestMapping("/getAllInfo")
    public ResultBean<HashMap<String, List>> getAllInfo(String pcId) {
        return service.getAllInfo(pcId);
    }

    @RequestMapping("/stop")
    public ResultBean<Boolean> stopTask(String pcId) {
        return service.stop(pcId);
    }
}
