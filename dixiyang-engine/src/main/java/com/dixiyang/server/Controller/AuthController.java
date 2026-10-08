package com.dixiyang.server.Controller;

import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.dto.AuthDTO;
import com.dixiyang.server.Entity.dto.EmailCodeDTO;
import com.dixiyang.server.Entity.dto.LoginByCodeDTO;
import com.dixiyang.server.Service.AuthService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * @author SuZiPing
 * @version 1.0
 */
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
        return authService.register(registerRequest);
    }

    @PostMapping("/send-code")
    public Result sendCode(@RequestBody EmailCodeDTO req) {
        return authService.sendCode(req.getEmail(), req.getPurpose());
    }

    @PostMapping("/login-by-code")
    public Result loginByCode(@RequestBody LoginByCodeDTO req) {
        return authService.loginByCode(req.getEmail(), req.getCode());
    }
}
