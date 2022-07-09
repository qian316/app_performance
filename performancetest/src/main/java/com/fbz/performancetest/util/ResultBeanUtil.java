package com.fbz.performancetest.util;


public class ResultBeanUtil {

    public static <T> ResultBean<T> success(T data){
        return new ResultBean<T>(true, data);
    }

    public static <T> ResultBean<T> success(){
        return new ResultBean<T>(true, ErrorEnum.SUCCESS);
    }

    public static <T> ResultBean<T> error(ErrorEnum commonEnum){
        return new ResultBean<T>(false, commonEnum);
    }


}
