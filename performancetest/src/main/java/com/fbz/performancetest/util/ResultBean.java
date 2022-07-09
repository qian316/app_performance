package com.fbz.performancetest.util;

import com.fbz.performancetest.util.ErrorEnum;

public class ResultBean<T> {
    private Boolean success;
    private String errorCode = "0000";//默认为0000，表示成功
    private String errorMessage;
    private T data;

    //成功时调用
    public ResultBean(Boolean success, T data) {
        this.success = success;
        this.data = data;
    }

    //失败时调用
    public ResultBean(Boolean success, ErrorEnum commonEnum){
        this.success = success;
        this.errorCode = commonEnum.getCode();
        this.errorMessage = commonEnum.getMessage();
    }

    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public String getErrorCode() {
        return errorCode;
    }

    public void setErrorCode(String errorCode) {
        this.errorCode = errorCode;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }
}
