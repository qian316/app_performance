package com.fbz.performancetest.config;

import com.fbz.performancetest.util.ErrorEnum;
import com.fbz.performancetest.util.ResultBean;
import com.fbz.performancetest.util.ResultBeanUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.ResponseStatus;

import javax.servlet.http.HttpServletRequest;

/**
 * @version: 1.0
 * @author: bozhou.fan
 * @create: 2022/4/13
 */
@ControllerAdvice
@Slf4j
class CommonExceptionHandler {

    /**
     *  自定义异常处理方法
     * @return
     */
    @ResponseBody
    @ResponseStatus(HttpStatus.OK)
    @ExceptionHandler(ConnectException.class)
    public ResultBean<Object> CommonExceptionHandler(ConnectException e, HttpServletRequest request) {
        return ResultBeanUtil.error(ErrorEnum.CONNECT_ERR) ;
    }

}
