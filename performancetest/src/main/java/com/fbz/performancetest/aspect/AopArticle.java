package com.fbz.performancetest.aspect;

import com.alibaba.fastjson.JSONObject;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.Signature;
import org.aspectj.lang.annotation.*;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import javax.servlet.http.HttpServletRequest;

@Slf4j
@Aspect
@Component
public class AopArticle {

//    private final Logger log = LoggerFactory.getLogger(this.getClass());

    @Pointcut("execution(* com.fbz.performancetest.controller..*.*(..))")
    public void point() {
    }

    // 前置通知
    @Before("point()")
    public void before(JoinPoint joinPoint) {
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        HttpServletRequest request = attributes.getRequest();

        StringBuilder requestLog = new StringBuilder();
        Signature signature = joinPoint.getSignature();
        requestLog.append("请求信息：").append("URL = {").append(request.getRequestURI()).append("},\t")
                .append("请求方式 = {").append(request.getMethod()).append("},\t")
                .append("请求IP = {").append(request.getRemoteAddr()).append("},\t")
                .append("类方法 = {").append(signature.getDeclaringTypeName()).append(".")
                .append(signature.getName()).append("},\t")
                .append("get请求url参数{").append(request.getQueryString()).append("},\t");

        // 处理请求参数
        String[] paramNames = ((MethodSignature) signature).getParameterNames();
        Object[] paramValues = joinPoint.getArgs();
        int paramLength = null == paramNames ? 0 : paramNames.length;
        if (paramLength == 0) {
            requestLog.append("请求参数 = {} ");
        } else {
            requestLog.append("请求参数 = [");
            for (int i = 0; i < paramLength - 1; i++) {
                requestLog.append(paramNames[i]).append("=").append(JSONObject.toJSONString(paramValues[i])).append(",");
            }
            requestLog.append(paramNames[paramLength - 1]).append("=").append(JSONObject.toJSONString(paramValues[paramLength - 1])).append("]");
        }

        log.info(requestLog.toString());
    }

    // 后置通知 始终会执行
    @After("point()")
    public void after() {
//        System.out.println("后置");
    }

    // 环绕通知
    @Around("point()")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
//        System.out.println("环绕前");
        Object result = pjp.proceed();
//        System.out.println("环绕后");
        return result;
    }

    // 后置 发生异常时不会执行
    @AfterReturning("point()")
    public void returning() {
//        System.out.println("After returning 后置");
    }

    // 发生异常
    @AfterThrowing("point()")
    public void throwing() {
//        System.out.println("发生异常了");
    }

}
