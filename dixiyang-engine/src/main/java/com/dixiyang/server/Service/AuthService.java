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
}
