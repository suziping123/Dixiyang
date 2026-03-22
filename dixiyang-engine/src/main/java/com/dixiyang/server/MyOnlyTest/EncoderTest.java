package com.dixiyang.server.MyOnlyTest;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

/**
 * @author SuZiPing
 * @version 1.0
 */
public class EncoderTest {
    public static void main(String[] args) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        String secret = encoder.encode("123456");
        System.out.println(secret);
        // 这一串贴到 MySQL 里了
    }

}
