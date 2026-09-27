package com.dixiyang.server.Service.My;

/**
 * @author SuZiPing
 * @version 1.0
 */
public class MyDaemonThread {
    public static void main(String[] args) throws InterruptedException {
        MyDaemon myDaemon = new MyDaemon();
        Thread thread = new Thread(myDaemon);
        thread.setDaemon(true);
        thread.start();
        for (int i = 0; i < 10; i++) {
            System.out.println("I'm a main thread.I'm working.王宝强在认证工作");
            Thread.sleep(500);
        }
    }
}

class MyDaemon implements Runnable{

    @Override
    public void run() {
        while(true) {
            try {
                Thread.sleep(1000);

            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
            System.out.println("I'm a daemon thread.马蓉和宋秸在聊天！");
        }
    }
}