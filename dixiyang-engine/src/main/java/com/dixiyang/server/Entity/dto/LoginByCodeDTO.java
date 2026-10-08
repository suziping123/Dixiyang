package com.dixiyang.server.Entity.dto;

import lombok.Data;

/**
 * 邮箱验证码登录请求
 */
@Data
public class LoginByCodeDTO {
    private String email;
    private String code;
}
