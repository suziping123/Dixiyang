package com.dixiyang.server.Entity.dto;
// 定义前端要给我啥？
import lombok.Data;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Data
public class AuthDTO {
    private String username;
    private String password; // 登录/注册必填
    private String nickname; // 注册必填，登录可不填
    private String email;    // 注册必填，登录可不填
}