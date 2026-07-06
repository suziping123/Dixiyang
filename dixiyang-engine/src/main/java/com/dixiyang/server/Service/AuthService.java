package com.dixiyang.server.Service;

import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.dto.AuthDTO;
import com.dixiyang.server.Entity.dto.VerifyCodeDTO;

public interface AuthService {
    Result<?> login(String username, String password);
    Result<?> register(AuthDTO authDTO);
    Result<?> sendCode(String email, String purpose);
    Result<?> loginByCode(VerifyCodeDTO dto);
    Result<?> registerByCode(AuthDTO authDTO, String code);
}
