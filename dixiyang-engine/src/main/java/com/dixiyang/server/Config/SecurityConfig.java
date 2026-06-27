/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-18 13:35:56
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-23 20:27:04
 * @FilePath: \Dixiyang\dixiyang-engine\src\main\java\com\dixiyang\server\Config\SecurityConfig.java
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
package com.dixiyang.server.Config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Autowired
    private JwtAuthenticationFilter jwtAuthenticationFilter;
    @Bean
    public PasswordEncoder passwordEncoder() {
        // 使用 BCrypt 强哈希算法来加密密码
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                // 1. 关闭 CSRF（开发环境登录接口必关，否则报 403）
                .csrf(csrf -> csrf.disable())
                // 2. 配置跨域允许（或者依赖 Vite 的 proxy，但后端不能报 302）
                .cors(Customizer.withDefaults())
                .authorizeHttpRequests(auth -> auth
                        // 3. 允许所有人访问公开接口（注意路径要匹配你的 Controller）
                        .requestMatchers("/user/**","/novel/**","/auth/**","/chat/**","/novelCharacter/**","/timeline/**","/storyNode/**","/upload/**","/uploads/**","/error").permitAll()
                        .anyRequest().authenticated()
                )
                .addFilterBefore(jwtAuthenticationFilter,
                        org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter.class)
                // 4. 关键：禁用默认的表单登录，防止它自动重定向到 /login
                .formLogin(form -> form.disable())
                .httpBasic(basic -> basic.disable());

        return http.build();
    }
}
