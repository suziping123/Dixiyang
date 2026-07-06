package com.dixiyang.server.Mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.dixiyang.server.Entity.EmailVerificationCode;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface EmailVerificationCodeMapper extends BaseMapper<EmailVerificationCode> {
}
