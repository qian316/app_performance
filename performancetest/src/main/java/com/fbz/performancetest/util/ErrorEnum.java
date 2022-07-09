package com.fbz.performancetest.util;

public enum ErrorEnum {

    SUCCESS("0000", "请求成功"),

    CONNECT_ERR("-1000", "连接失败");

    private String code;
    private String message;

    private ErrorEnum(String code, String message) {
        this.code = code;
        this.message = message;
    }

    public String getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }
}
