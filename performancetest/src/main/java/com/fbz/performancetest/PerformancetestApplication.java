package com.fbz.performancetest;

import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.util.concurrent.ConcurrentHashMap;
@Slf4j
@SpringBootApplication
public class PerformancetestApplication {

    //所有的内存对象和合集
    public static final ConcurrentHashMap<String, Object> objectMap = new ConcurrentHashMap<>();
    /**concurrent包的线程安全Set，用来存放每个客户端对应的WebSocket对象。*/
//    public static final ConcurrentHashMap<String, WebSocketServer> webSocketMap = new ConcurrentHashMap<>();


    public static void main(String[] args) {
        log.info("run");
        System.out.println(System.getProperty("os.name"));
        System.out.println(System.getProperty("user.dir"));
        SpringApplication.run(PerformancetestApplication.class, args);
    }

}
