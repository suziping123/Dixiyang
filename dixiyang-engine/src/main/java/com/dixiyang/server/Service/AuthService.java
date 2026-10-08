package com.dixiyang.server.Service;
import com.dixiyang.server.Common.Result; // 别忘了之前说的统一返回类
import com.dixiyang.server.Entity.dto.AuthDTO;

/**
 * @author SuZiPing
 * @version 1.0
 */
public interface AuthService {
    Result<Void> login(String username, String password);

    Result<Void> register(AuthDTO authDTO);

    /**
     * 邮箱验证码登录（风控解除口）
     */
    Result<Void> loginByCode(String email, String code);

    /**
     * 发送邮箱验证码（LOGIN/REGISTER/CHG_EMAIL）
     */
    Result<Void> sendCode(String email, String purpose);
}
