package com.fbz.performancetest;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.util.concurrent.ConcurrentHashMap;

@SpringBootApplication
public class PerformancetestApplication {

    //所有的内存对象和合集
    public static final ConcurrentHashMap<String, Object> objectMap = new ConcurrentHashMap<>();

    public static void main(String[] args) {
        SpringApplication.run(PerformancetestApplication.class, args);
    }

}
