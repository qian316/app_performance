package com.fbz.performancetest.util;

public class Device {
    private String host = "localhost";
    private Integer port = 5037;
    private String serial = null;

    public Device(String serial) {
        this.serial = serial;
    }

    public Device(Integer port, String serial) {
        this.port = port;
        this.serial = serial;
    }

    public Device(String host, Integer port, String serial) {
        this.host = host;
        this.port = port;
        this.serial = serial;
    }

    public String getHost() {
        return host;
    }

    public void setHost(String host) {
        this.host = host;
    }

    public Integer getPort() {
        return port;
    }

    public void setPort(Integer port) {
        this.port = port;
    }

    public String getSerial() {
        return serial;
    }

    public void setSerial(String serial) {
        this.serial = serial;
    }
}
