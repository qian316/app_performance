package com.fbz.performancetest.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AllController {

    @RequestMapping("/createtask")
    public int createTask(){
        return 1;
    }
}
