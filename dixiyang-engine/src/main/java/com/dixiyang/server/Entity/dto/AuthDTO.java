package com.dixiyang.server.Entity.dto;

import lombok.Data;

@Data
public class AuthDTO {
    private String username;
    private String password;
    private String nickname;
    private String email;
    private String code; // 验证码（注册时使用）
}
