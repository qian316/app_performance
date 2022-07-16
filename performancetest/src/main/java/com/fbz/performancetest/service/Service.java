package com.fbz.performancetest.service;

import com.fbz.performancetest.util.ResultBean;

import java.util.HashMap;
import java.util.List;

public interface Service {

    ResultBean<Boolean> connect(String pcId, String host, Integer port, String serial);

    ResultBean<String []> getAllPackage(String pcId, String host, Integer port, String serial);

    ResultBean<String> start(String pcId, String host, Integer port, String serial, String packageName);

    ResultBean<Boolean> stop(String pcId);

    ResultBean<HashMap<String, List>> getAllInfo(String pcId);
}
