package com.dixiyang.server.Entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 邮箱验证码（与 DixyangFast models/email_verification.py 共表）
 * 时间字段一律存 UTC 字面值，与 Python 端保持一致
 */
@Data
@TableName("email_verification_code")
public class EmailVerificationCode {
    @TableId(type = IdType.AUTO)
    private Integer id;
    //    收件邮箱
    private String email;
    //    6位数字验证码
    private String code;
    //    用途：LOGIN/REGISTER/CHG_EMAIL
    private String purpose;
    //    过期时间（UTC）
    private LocalDateTime expireTime;
    //    是否已使用（一次性）
    private Boolean used;
    //    创建时间（UTC，用于60秒限流）
    private LocalDateTime createdAt;
}
