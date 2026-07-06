package com.dixiyang.server.Service;

public interface EmailService {
    void sendVerificationCode(String to, String code);
}
