package com.dixiyang.server.Service;

import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.dto.AuthDTO;
import com.dixiyang.server.Entity.dto.VerifyCodeDTO;

public interface AuthService {
    Result<Void> login(String username, String password);
    Result<Void> register(AuthDTO authDTO);
    Result<Void> sendCode(String email, String purpose);
    Result<Void> loginByCode(VerifyCodeDTO dto);
    Result<Void> registerByCode(AuthDTO authDTO, String code);
}
