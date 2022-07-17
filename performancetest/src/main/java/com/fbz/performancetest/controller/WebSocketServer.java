package com.fbz.performancetest.controller;

import com.fbz.performancetest.PerformancetestApplication;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import javax.websocket.*;
import javax.websocket.server.PathParam;
import javax.websocket.server.ServerEndpoint;
import java.io.IOException;
import java.util.ArrayList;
import java.util.concurrent.ConcurrentHashMap;

/**
 * websocket的处理类。
 * 作用相当于HTTP请求
 * 中的controller
 */
@Component
@Slf4j
@ServerEndpoint("/send/{pcId}")
public class WebSocketServer {

    /**concurrent包的线程安全Set，用来存放每个客户端对应的WebSocket对象。*/
    private static ConcurrentHashMap<String,WebSocketServer> webSocketMap = PerformancetestApplication.webSocketMap;
    public ArrayList<String> clientMessage = new ArrayList<>();
    /**与某个客户端的连接会话，需要通过它来给客户端发送数据*/
    private Session session;
    /**接收userId*/
    private String cpId = "";

    /**
     * 连接建立成
     * 功调用的方法
     */
    @OnOpen
    public void onOpen(Session session, @PathParam("pcId") String pcId) {
        this.session = session;
        this.cpId = pcId;
        if (webSocketMap.containsKey(pcId)) {
            webSocketMap.remove(pcId);
            //加入set中
            webSocketMap.put(pcId, this);
        } else {
            //加入set中
            webSocketMap.put(pcId, this);
        }
        System.out.println(String.format("connect %s", pcId));
    }

    /**
     * 连接关闭
     * 调用的方法
     */
    @OnClose
    public void onClose() {
        if(webSocketMap.containsKey(cpId)){
            webSocketMap.remove(cpId);
            //从set中删除
        }
    }

    /**
     * 收到客户端消
     * 息后调用的方法
     * @param message
     * 客户端发送过来的消息
     **/
    @OnMessage
    public void onMessage(String message, Session session) throws InterruptedException {
        System.out.println(String.format("recv %s", message));
        this.clientMessage.add(message);
    }


    /**
     * @param session
     * @param error
     */
    @OnError
    public void onError(Session session, Throwable error) {

        log.error("用户错误:"+this.cpId+",原因:"+error.getMessage());
        error.printStackTrace();
    }

    /**
     * 实现服务
     * 器主动推送
     */
    public void sendMessage(String message) {
        System.out.println(String.format("server send %s", message));
        try {
            this.session.getBasicRemote().sendText(message);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}

