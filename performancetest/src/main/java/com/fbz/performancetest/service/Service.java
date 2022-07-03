package com.fbz.performancetest.service;

import java.util.List;
import java.util.Map;

public interface Service {
    String start(String pcId, String host, Integer port, String serial, String packageName);

    boolean stop(String pcId);

    Map<String, List> getAllInfo(String pcId);
}
