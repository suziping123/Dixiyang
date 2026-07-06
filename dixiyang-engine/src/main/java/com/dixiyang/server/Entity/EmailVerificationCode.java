package com.dixiyang.server.Entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("email_verification_code")
public class EmailVerificationCode {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String email;
    private String code;
    private String purpose; // LOGIN or REGISTER
    private LocalDateTime expireTime;
    private Boolean used;
    private LocalDateTime createdAt;
}
