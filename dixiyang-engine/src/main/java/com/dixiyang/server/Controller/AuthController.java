package com.dixiyang.server.Controller;

import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.dto.AuthDTO;
import com.dixiyang.server.Entity.dto.VerifyCodeDTO;
import com.dixiyang.server.Service.AuthService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@Tag(name = "身份认证模块")
public class AuthController {
    @Autowired
    private AuthService authService;

    @PostMapping("/login")
    public Result login(@RequestBody AuthDTO loginRequest) {
        return authService.login(loginRequest.getUsername(), loginRequest.getPassword());
    }

    @PostMapping("/register")
    public Result register(@RequestBody AuthDTO registerRequest) {
        if (registerRequest.getCode() != null && !registerRequest.getCode().isBlank()) {
            return authService.registerByCode(registerRequest, registerRequest.getCode());
        }
        return authService.register(registerRequest);
    }

    @PostMapping("/send-code")
    public Result sendCode(@RequestBody java.util.Map<String, String> body) {
        String email = body.get("email");
        String purpose = body.getOrDefault("purpose", "LOGIN");
        return authService.sendCode(email, purpose);
    }

    @PostMapping("/login-by-code")
    public Result loginByCode(@RequestBody VerifyCodeDTO dto) {
        return authService.loginByCode(dto);
    }
}
