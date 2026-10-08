package com.dixiyang.server.Entity.dto;

import lombok.Data;

/**
 * 邮箱验证码请求（发送）
 */
@Data
public class EmailCodeDTO {
    private String email;
    //    用途：LOGIN/REGISTER/CHG_EMAIL
    private String purpose;
}
